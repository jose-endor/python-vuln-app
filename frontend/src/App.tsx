import React, { useCallback, useEffect, useState } from "react";
import axios from "axios";
import type { Book, Me } from "./types";
import { probeOptionalDependency } from "./supplyProbe";

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
  const [depName, setDepName] = useState("event-stream");
  const [depProbe, setDepProbe] = useState("");

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

  const runDepProbe = async () => {
    setErr("");
    const r = await probeOptionalDependency(depName);
    setDepProbe(r);
  };

  return (
    <div className="page">
      <header className="hero">
        <p className="kicker">Stack &amp; Spine</p>
        <h1>Your next read is on the shelf.</h1>
        <p className="lede">
          Browse what we have in store; sign in for members&apos; hold requests and order notes.
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
          <h3 className="subh">Partner extension check</h3>
          <p className="small muted">Runtime probe for optional JS packages listed in supplemental manifests.</p>
          <div className="form">
            <input
              className="inline"
              value={depName}
              onChange={(e) => setDepName(e.target.value)}
              placeholder="event-stream"
            />
            <button type="button" className="btn-ghost small-btn" onClick={() => void runDepProbe()}>
              Probe module import
            </button>
            {depProbe && <p className="small muted">{depProbe}</p>}
          </div>
        </aside>
      </div>

      <footer className="subfoot">Curbside · special orders · gift wrap when we are not too slammed.</footer>
    </div>
  );
};
