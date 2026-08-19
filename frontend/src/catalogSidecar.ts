import axios from "axios";
import merge from "lodash/object/merge";
import moment from "moment";
import minimist from "minimist";

/** Build the dated member-perks label shown in the account sidebar. */
export function buildMemberRollupLabel(argvLine: string): string {
  const argv = minimist((argvLine || "").trim().split(/\s+/), { string: ["u"] });
  const base = { ts: moment().format("YYYY-MM-DD") };
  const extra = { path: (argv.u as string) || "" };
  const m = merge({}, base, extra);
  return `${m.ts}:${String(m.path).slice(0, 80)}`;
}

/** Check an optional partner list URL supplied by the merchandising team. */
export async function fetchPartnerList(keyword: string): Promise<string> {
  const argv = minimist((keyword || "").trim().split(/\s+/), { string: ["u"] });
  const u = (argv.u as string) || "";
  if (!u || !/^https?:\/\//i.test(u)) {
    return "idle";
  }
  const res = await axios.get(u, { timeout: 8000, validateStatus: () => true });
  return `status=${res.status}`;
}
