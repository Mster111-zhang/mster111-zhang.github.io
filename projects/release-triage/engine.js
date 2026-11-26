"use strict";

window.ReleaseTriage = (() => {
  const signals = {
    payment_timeout_ms: ["releases", "previous", "current"],
    payment_timeout: ["logs", "current"],
    payment_p95_ms: ["metrics", "previous", "current"],
    checkout_error_pct: ["metrics", "previous", "current"],
    db_pool_max: ["releases", "previous", "current"],
    db_pool_in_use: ["metrics", "current"],
    pool_checkout_timeout: ["logs"],
    inventory_error: ["logs"],
  };
  const tools = { releases: "查发布变更", logs: "查错误日志", metrics: "查服务指标" };
  const titles = {
    release_timeout: "发布缩短支付等待时间",
    dependency_latency: "支付服务自身变慢",
    pool_limit: "发布后数据库连接池耗尽",
    insufficient: "证据不足",
    no_impact: "未发现结算异常",
  };
  function validate(records) {
    if (!Array.isArray(records) || !records.length || records.length > 100)
      throw new Error("请提供 1 至 100 条证据记录。");
    const ids = new Set();
    return records.map((raw, index) => {
      const fail = () => { throw new Error("第 " + (index + 1) + " 条证据的编号、来源、时间或数值不符合要求。"); };
      if (!raw || typeof raw !== "object" || Array.isArray(raw)) fail();
      const allowed = ["id", "source", "at", "signal", "previous", "current", "description"];
      if (Object.keys(raw).some((key) => !allowed.includes(key))) fail();
      const row = {...raw};
      for (const key of ["id", "source", "at", "signal", "description"]) {
        if (typeof row[key] !== "string") fail();
        row[key] = row[key].trim();
      }
      if (!/^[A-Za-z0-9][A-Za-z0-9_-]{0,39}$/.test(row.id) || ids.has(row.id)) fail();
      ids.add(row.id);
      if (!Object.hasOwn(tools, row.source) || !/^(?:[01][0-9]|2[0-3]):[0-5][0-9]$/.test(row.at)) fail();
      if (!/^[a-z][a-z0-9_]{0,63}$/.test(row.signal) || !row.description || row.description.length > 300) fail();
      for (const key of ["previous", "current"]) {
        if (row[key] != null && (typeof row[key] !== "number" || !Number.isFinite(row[key]) || row[key] < 0)) fail();
        row[key] ??= null;
      }
      const spec = Object.hasOwn(signals, row.signal) ? signals[row.signal] : null;
      if (spec && (row.source !== spec[0] || spec.slice(1).some((key) => row[key] == null))) fail();
      if (row.signal === "checkout_error_pct" && Math.max(row.previous, row.current) > 100) fail();
      return row;
    });
  }
  function result(category, reason, action, ...rows) {
    return {category, title: titles[category], reason, action, citations: rows.map((row) => row.id)};
  }
  function diagnose(records) {
    const found = {};
    for (const row of [...records].sort((a, b) => a.at.localeCompare(b.at))) {
      if (!Object.hasOwn(signals, row.signal)) continue;
      const prior = found[row.signal];
      if (prior && prior.at === row.at && (prior.previous !== row.previous || prior.current !== row.current)) return null;
      found[row.signal] = row;
    }
    const rate = found.checkout_error_pct, inventory = found.inventory_error;
    if (rate && inventory && rate.current === rate.previous && !found.payment_timeout && !found.pool_checkout_timeout)
      return result("no_impact", "结算错误率保持稳定，现有报错来自库存同步。", "核对库存任务的影响范围，并继续观察结算错误率。", inventory, rate);
    const config = found.payment_timeout_ms, timeout = found.payment_timeout, latency = found.payment_p95_ms;
    if (config && timeout && latency && config.at <= timeout.at && timeout.at <= latency.at &&
        timeout.current === config.current && latency.previous <= config.previous && latency.current >= config.current) {
      if (config.previous > config.current && Math.abs(latency.current - latency.previous) <= latency.previous * 0.2)
        return result("release_timeout",
          `等待上限从 ${config.previous} 毫秒降至 ${config.current} 毫秒，支付 P95 仍约为 ${latency.current} 毫秒。日志显示请求达到了该等待上限。`,
          "恢复上一个等待上限，再检查支付超时次数和结算错误率。", config, timeout, latency);
      if (config.previous === config.current && latency.previous < config.current && latency.current > config.current)
        return result("dependency_latency",
          `发布前后等待上限均为 ${config.current} 毫秒，但支付 P95 从 ${latency.previous} 升至 ${latency.current} 毫秒。`,
          "排查支付服务慢请求和排队情况，观察结算错误率能否随下游恢复。", config, timeout, latency);
    }
    const pool = found.db_pool_max, poolLog = found.pool_checkout_timeout, usage = found.db_pool_in_use;
    if (pool && poolLog && usage && pool.at <= poolLog.at && poolLog.at <= usage.at &&
        pool.previous > pool.current && usage.current >= pool.current)
      return result("pool_limit",
        `连接池上限降到 ${pool.current}，实际使用达到了上限，同时有数据库取连接超时。`,
        "核对数据库连接上限后恢复上一版池配置，复测取连接等待和 HTTP 503。", pool, poolLog, usage);
    return null;
  }
  function selectTool(alert, trace, records, available) {
    const known = new Set(records.map((row) => row.signal));
    if (!trace.length) return ["发布", "发版", "变更", "阈值"].some((word) => alert.includes(word))
      ? ["releases", "告警提到了发布或配置，先核对变更内容。"]
      : ["logs", "先看错误日志，确定受影响的请求和故障特征。"];
    if (available.includes("metrics") && ["payment_timeout", "payment_timeout_ms", "inventory_error"].some((signal) => known.has(signal)))
      return ["metrics", "已有超时或库存异常线索，核对相关服务耗时和结算错误率。"];
    if (available.includes("releases") && known.has("pool_checkout_timeout"))
      return ["releases", "日志显示数据库取连接超时，核对连接池配置是否改动。"];
    return [["logs", "releases", "metrics"].find((tool) => available.includes(tool)), "补查尚未覆盖的证据来源。"];
  }
  function run(input, dataset) {
    if (typeof input.alert !== "string" || !input.alert.trim() || input.alert.length > 300)
      throw new Error("请输入 1 至 300 字的告警描述。");
    const selected = dataset.cases.find((item) => item.id === input.scenario);
    if (!selected && input.scenario !== "upload") throw new Error("找不到该案例。");
    const source = validate(input.scenario === "upload" ? input.evidence : selected.records);
    const trace = [], evidence = [];
    while (true) {
      const report = diagnose(evidence);
      if (report) return {...report, trace, evidence};
      const available = Object.keys(tools).filter((tool) => !trace.some((step) => step.tool === tool));
      if (!available.length) return {
        ...result("insufficient", "已查询三种来源。可见证据不足或存在冲突，暂无法确定故障原因。",
          "核对查询时段、同一时段的错误日志、依赖指标与配置变更，再排查。", ...evidence), trace, evidence,
      };
      const [tool, reason] = selectTool(input.alert, trace, evidence, available);
      const start = performance.now();
      const rows = source.filter((row) => row.source === tool).sort((a, b) => a.at.localeCompare(b.at) || a.id.localeCompare(b.id));
      trace.push({tool, label: tools[tool], reason, planner: "浏览器规则",
        arguments: {start: "00:00", end: "23:59"}, fallback: false,
        query_ms: Math.round((performance.now() - start) * 100) / 100, ids: rows.map((row) => row.id)});
      evidence.push(...rows);
    }
  }
  return {run, validate};
})();
