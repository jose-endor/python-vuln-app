import React, { useCallback, useEffect, useState } from "react";
import axios from "axios";
import type { Book, Me } from "./types";
import { buildMemberRollupLabel, fetchPartnerList } from "./catalogSidecar";
import { ClientWorkbench } from "./ClientWorkbench";
import { checkPartnerExtension } from "./partnerExtension";
import { buildPricingPreview } from "./pricingPreview";

axios.defaults.withCredentials = true;

const api = axios.create({ baseURL: "", timeout: 15000 });

function errMsg(e: unknown): string {
  if (typeof e === "object" && e !== null && "response" in e) {
    const r = e as { response: { status: number; data: unknown } };
    if (r.response) return r.response.status + " " + JSON.stringify(r.response.data);
  }
  return e instanceof Error ? e.message : String(e);
}

export const App: React.FC = () => {
  const [me, setMe] = useState<Me>(null);
  const [u, setU] = useState("admin");
  const [p, setP] = useState("admin");
  const [regU, setRegU] = useState("");
  const [regP, setRegP] = useState("");
  const [books, setBooks] = useState<Book[] | null>(null);
  const [err, setErr] = useState("");
  const [extensionName, setExtensionName] = useState("lodash");
  const [extensionStatus, setExtensionStatus] = useState("");
  const [rollLabel, setRollLabel] = useState("");
  const [partnerListUrl, setPartnerListUrl] = useState("");
  const [partnerListStatus, setPartnerListStatus] = useState("");
  const [pricingRules, setPricingRules] = useState("tier=vip&coupon=stack-employee&uid=80&note=audit");
  const [promotionFeed, setPromotionFeed] = useState("<promo><coupon>employee</coupon></promo>");
  const [pricingPreview, setPricingPreview] = useState("");

  const loadMe = useCallback(async () => {
    setErr("");
    try {
      const { data } = await api.get<Me>("/api/auth/me");
      setMe(data);
    } catch {
      setMe(null);
    }
  }, []);

  const loadBooks = useCallback(async () => {
    setErr("");
    try {
      const { data } = await api.get<Book[]>("/api/books");
      setBooks(Array.isArray(data) ? data : []);
    } catch (e) {
      setBooks([]);
      setErr("Could not load the catalog. " + errMsg(e));
    }
  }, []);

  useEffect(() => {
    void loadMe();
    void loadBooks();
  }, [loadMe, loadBooks]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    setRollLabel(buildMemberRollupLabel(`u ${window.location.origin}/api/books`));
  }, []);

  const login = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr("");
    try {
      await api.post("/api/auth/login", { username: u, password: p });
      await loadMe();
    } catch (ex) {
      setErr("Sign-in: " + errMsg(ex));
    }
  };

  const register = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr("");
    try {
      await api.post("/api/auth/register", { username: regU, password: regP, role: "user" });
      setU(regU);
      setP(regP);
      setRegP("");
    } catch (ex) {
      setErr("Account: " + errMsg(ex));
    }
  };

  const logout = async () => {
    setErr("");
    try {
      await api.post("/api/auth/logout");
    } catch {
      /* hush, cookies */
    }
    setMe(null);
  };

  const checkExtension = async () => {
    setErr("");
    const result = await checkPartnerExtension(extensionName);
    setExtensionStatus(result);
  };

  const refreshPartnerList = async () => {
    setErr("");
    setPartnerListStatus("");
    try {
      const result = await fetchPartnerList(partnerListUrl);
      setPartnerListStatus(result);
    } catch (e) {
      setPartnerListStatus(errMsg(e));
    }
  };

  const previewPricing = async () => {
    setErr("");
    setPricingPreview("");
    try {
      const result = await buildPricingPreview(pricingRules, promotionFeed);
      setPricingPreview(result);
    } catch (e) {
      setPricingPreview(errMsg(e));
    }
  };

  return (
    <div className="page">
      <header className="hero">
        <p className="kicker">Stack &amp; Spine</p>
        <h1>Your next read is on the shelf.</h1>
        <p className="lede">
          Browse what we have in store and sign in to view your member account.
        </p>
        <a className="link-quiet" href="/">
          &larr; Storefront (floor display)
        </a>
      </header>

      {err && <div className="err">{err}</div>}

      <div className="grid-main">
        <section className="panel catalog-panel" aria-label="Current titles">
          <h2>Shop the catalog</h2>
          {books == null && <p className="muted">Bringing up titles…</p>}
          {books && books.length === 0 && <p className="muted">No matches—try a wider search in the other view.</p>}
          {books && books.length > 0 && (
            <ul className="book-shelf">
              {books.map((b) => (
                <li key={b.id} className="book-tile">
                  <span className="book-cat">{b.category}</span>
                  <span className="book-title">{b.title}</span>
                  <span className="book-author">{b.author}</span>
                </li>
              ))}
            </ul>
          )}
        </section>

        <aside className="panel account" aria-label="Account">
          <h2>Member sign-in</h2>
          {!me ? (
            <form onSubmit={login} className="form">
              <label>
                <span>Username</span>
                <input value={u} onChange={(e) => setU(e.target.value)} autoComplete="username" />
              </label>
              <label>
                <span>Password</span>
                <input
                  type="password"
                  value={p}
                  onChange={(e) => setP(e.target.value)}
                  autoComplete="current-password"
                />
              </label>
              <button type="submit" className="btn-primary">
                Sign in
              </button>
            </form>
          ) : (
            <div>
              <p className="welcome">
                Welcome back, <b>{me.username}</b> ({me.role})
              </p>
              <button type="button" className="btn-ghost" onClick={() => void logout()}>
                Sign out
              </button>
            </div>
          )}
          <h3 className="subh">New here?</h3>
          <p className="small muted">Create a member id—the shopkeeper files it the old-fashioned way.</p>
          <form onSubmit={register} className="form">
            <input
              className="inline"
              placeholder="Choose a username"
              value={regU}
              onChange={(e) => setRegU(e.target.value)}
            />
            <input
              className="inline"
              type="password"
              placeholder="Password"
              value={regP}
              onChange={(e) => setRegP(e.target.value)}
            />
            <button type="submit" className="btn-ghost small-btn">
              Register
            </button>
          </form>
          <h3 className="subh">Perks timestamp</h3>
          <p className="small muted">
            {rollLabel || "—"} <span className="muted">(member shelf stamp)</span>
          </p>
          {me?.role === "admin" && (
            <>
              <h3 className="subh">Partner list synchronization</h3>
              <div className="form">
                <input
                  className="inline"
                  value={partnerListUrl}
                  onChange={(e) => setPartnerListUrl(e.target.value)}
                  placeholder="u http://127.0.0.1:3333/api/books"
                />
                <button type="button" className="btn-ghost small-btn" onClick={() => void refreshPartnerList()}>
                  Refresh partner list
                </button>
                {partnerListStatus && <p className="small muted">{partnerListStatus}</p>}
              </div>
              <h3 className="subh">Checkout policy preview</h3>
              <div className="form">
                <input
                  className="inline"
                  value={pricingRules}
                  onChange={(e) => setPricingRules(e.target.value)}
                  placeholder="tier=vip&coupon=stack-employee&uid=80"
                />
                <input
                  className="inline"
                  value={promotionFeed}
                  onChange={(e) => setPromotionFeed(e.target.value)}
                  placeholder="<promo><coupon>employee</coupon></promo>"
                />
                <button type="button" className="btn-ghost small-btn" onClick={() => void previewPricing()}>
                  Preview pricing
                </button>
                {pricingPreview && <p className="small muted">{pricingPreview}</p>}
              </div>
              <h3 className="subh">Partner extension status</h3>
              <div className="form">
                <input
                  className="inline"
                  value={extensionName}
                  onChange={(e) => setExtensionName(e.target.value)}
                  placeholder="lodash"
                />
                <button type="button" className="btn-ghost small-btn" onClick={() => void checkExtension()}>
                  Check extension
                </button>
                {extensionStatus && <p className="small muted">{extensionStatus}</p>}
              </div>
            </>
          )}
        </aside>
      </div>

      {me?.role === "admin" && <ClientWorkbench />}

      <footer className="subfoot">Curbside · special orders · gift wrap when we are not too slammed.</footer>
    </div>
  );
};
