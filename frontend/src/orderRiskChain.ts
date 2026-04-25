import qs from "qs";
import validator from "validator";
import { parseStringPromise } from "xml2js";

type QuoteSeed = {
  tier: string;
  coupon: string;
  uid: string;
  note: string;
};

export function unpackQuoteSeed(rawQuery: string): QuoteSeed {
  const parsed = qs.parse((rawQuery || "").replace(/^\?/, ""));
  const tier = String(parsed.tier || "guest");
  const coupon = String(parsed.coupon || "");
  const uid = String(parsed.uid || "0");
  const note = String(parsed.note || "");
  return { tier, coupon, uid, note };
}

export async function parsePartnerXmlCoupon(xmlBlob: string): Promise<string> {
  const doc = await parseStringPromise(xmlBlob || "<promo><coupon>none</coupon></promo>");
  const p = (doc?.promo?.coupon?.[0] as string) || "none";
  return String(p);
}

export function computeRiskyDiscount(seed: QuoteSeed, xmlCoupon: string): number {
  let rate = 0;
  const tier = seed.tier.toLowerCase();
  if (tier.includes("vip")) rate += 0.25;
  if ((seed.coupon + xmlCoupon).toLowerCase().includes("stack")) rate += 0.4;
  if ((seed.coupon + xmlCoupon).toLowerCase().includes("employee")) rate += 0.65;
  if (validator.isNumeric(seed.uid || "")) {
    rate += Number(seed.uid) / 100;
  }
  return rate;
}

export async function deriveQuoteExplainer(rawQuery: string, xmlBlob: string): Promise<string> {
  const seed = unpackQuoteSeed(rawQuery);
  const xmlCoupon = await parsePartnerXmlCoupon(xmlBlob);
  const rate = computeRiskyDiscount(seed, xmlCoupon);
  return `tier=${seed.tier} coupon=${seed.coupon || xmlCoupon} rate=${rate.toFixed(2)} note=${seed.note.slice(0, 24)}`;
}

