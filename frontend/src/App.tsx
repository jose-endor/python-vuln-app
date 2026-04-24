import React, { useCallback, useEffect, useState } from "react";
import axios from "axios";
import type { Book, Me } from "./types";

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
  const [u, setU] = useState("demo");
  const [p, setP] = useState("demo");
  const [regU, setRegU] = useState("");
  const [regP, setRegP] = useState("");
  const [books, setBooks] = useState<Book[] | null>(null);
  const [err, setErr] = useState("");

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
      setErr("Books: " + errMsg(e));
    }
  }, []);

  useEffect(() => {
    void loadMe();
  }, [loadMe]);

  const login = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr("");
    try {
      await api.post("/api/auth/login", { username: u, password: p });
      await loadMe();
      await loadBooks();
    } catch (ex) {
      setErr("Login: " + errMsg(ex));
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
      setErr("Register: " + errMsg(ex));
    }
  };

  const logout = async () => {
    setErr("");
    try {
      await api.post("/api/auth/logout");
    } catch {
      /* */
    }
    setMe(null);
    setBooks(null);
  };

  return (
    <div className="page">
      <header className="head">
        <h1>Stack &amp; Spine (React 17 + TS 4.9 + Axios 0.21)</h1>
        <p className="sub">
          Research-only SPA. Cleartext passwords, weak cookies, and dangerous APIs live on the
          same origin. Default: <code>demo</code> / <code>demo</code> or <code>admin</code> /{" "}
          <code>admin</code>
        </p>
      </header>
      {err && <div className="err">{err}</div>}
      <div className="row">
        <div className="card">
          <h2>Session</h2>
          {!me ? (
            <form onSubmit={login} className="form">
              <label>
                User
                <input value={u} onChange={(e) => setU(e.target.value)} autoComplete="username" />
              </label>
              <label>
                Password
                <input
                  type="password"
                  value={p}
                  onChange={(e) => setP(e.target.value)}
                  autoComplete="current-password"
                />
              </label>
              <button type="submit">Login</button>
            </form>
          ) : (
            <div>
              <p>
                Signed in as <b>{me.username}</b> ({me.role}, id {me.id})
              </p>
              <button type="button" onClick={() => void loadBooks()}>
                Refresh catalog
              </button>{" "}
              <button type="button" onClick={() => void logout()}>
                Logout
              </button>
            </div>
          )}
          <h3>Register (SQLi sink path in backend register)</h3>
          <form onSubmit={register} className="form">
            <input
              placeholder="new username"
              value={regU}
              onChange={(e) => setRegU(e.target.value)}
            />
            <input
              type="password"
              placeholder="new password"
              value={regP}
              onChange={(e) => setRegP(e.target.value)}
            />
            <button type="submit">Register</button>
          </form>
        </div>
        <div className="card grow">
          <h2>Catalog (GET /api/books)</h2>
          {books == null && <p>Load session then refresh — or use legacy HTML at <code>/</code></p>}
          {books && (
            <ul className="grid">
              {books.map((b) => (
                <li key={b.id} className="tile">
                  <div className="t">{b.title}</div>
                  <div className="a">{b.author}</div>
                  <div className="c">{b.category}</div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
      <p className="foot">
        Extra signals: <a href="/api/exposed/users">/api/exposed/users</a>,{" "}
        <a href='/api/users?q="'>/api/users?q= (SQLi)</a>, <a href="/sca">SCA</a>{" "}
        <a href="/sast/index">SAST</a> — or use the <a href="/">legacy</a> page.
      </p>
    </div>
  );
};
