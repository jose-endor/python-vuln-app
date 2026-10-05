# Dependency verdicts (200 npm packages)

Per-package results from the Endor Labs `check_dependency_for_risks` MCP tool (vulnerability and malware lookup by name and exact version). Ecosystem: npm. Date: 2026-10-02/03 UTC.

- Packages checked: 200
- Tool errors / invalid versions: 0
- Malware flagged: 0
- Vulnerable: 106
- Clean: 94
- Advisory IDs returned: 345 (not deduplicated, e.g. lodash and lodash.template share CVE-2026-4800)

Notes on reading this table:
- "Advisories" is the count of advisory IDs the tool returned for that exact version. The tool returns no severity or reachability, so this file does not rank by severity. See scan-results.md for reachability-aware findings from the full scan.
- "none" means the version is vulnerable and the tool offered no version without known vulnerabilities.
- "prerelease only" means the only recommended upgrade is an alpha/beta/rc/dev build, which is usually not a safe production pick.
- Only direct dependencies were checked here. Transitive dependencies are covered by the full scan.

## Vulnerable (106)

| Package | Version | Advisories | Verdict | Recommended upgrade |
|---|---|---|---|---|
| axios | 0.21.0 | 20 | VULNERABLE | 0.34.0 |
| nodemailer | 6.4.0 | 17 | VULNERABLE | 10.0.13 |
| xmldom | 0.1.27 | 17 | VULNERABLE | none |
| dompurify | 2.0.8 | 16 | VULNERABLE | 3.4.16 |
| node-forge | 0.9.0 | 15 | VULNERABLE | none |
| tar | 4.4.0 | 15 | VULNERABLE | 7.5.22 |
| angular | 1.7.0 | 13 | VULNERABLE | none |
| handlebars | 4.5.0 | 12 | VULNERABLE | 4.7.9 |
| brace-expansion | 1.1.8 | 9 | VULNERABLE | 2.1.7 |
| elliptic | 6.5.0 | 9 | VULNERABLE | none |
| multer | 1.4.0 | 8 | VULNERABLE | 2.4.0 |
| bootstrap | 3.3.7 | 7 | VULNERABLE | 5.3.8 |
| sanitize-html | 1.20.0 | 7 | VULNERABLE | 2.18.0 |
| webpack-dev-server | 3.9.0 | 6 | VULNERABLE | 6.0.0 |
| js-yaml | 3.13.0 | 5 | VULNERABLE | 5.4.2 |
| mongoose | 5.9.0 | 5 | VULNERABLE | 9.10.3 |
| postcss | 7.0.21 | 5 | VULNERABLE | 8.5.28 |
| prismjs | 1.17.1 | 5 | VULNERABLE | 2.0.0-alpha.1 (prerelease only) |
| sequelize | 5.21.0 | 5 | VULNERABLE | 6.37.8 |
| follow-redirects | 1.5.10 | 4 | VULNERABLE | 1.16.1 |
| lodash | 4.17.15 | 4 | VULNERABLE | 4.18.1 |
| minimatch | 3.0.4 | 4 | VULNERABLE | 10.2.6 |
| morgan | 1.9.0 | 4 | VULNERABLE | 1.12.1 |
| showdown | 1.9.0 | 4 | VULNERABLE | none |
| crypto-js | 3.1.9-1 | 3 | VULNERABLE | 4.2.0 |
| grunt | 1.0.0 | 3 | VULNERABLE | 1.6.3 |
| immutable | 3.8.2 | 3 | VULNERABLE | 6.0.0-beta.1 (prerelease only) |
| jose | 2.0.0 | 3 | VULNERABLE | 6.2.12 |
| jsonwebtoken | 8.5.0 | 3 | VULNERABLE | 9.0.3 |
| lodash.defaultsdeep | 4.6.0 | 3 | VULNERABLE | 4.6.1 |
| markdown-it | 8.4.2 | 3 | VULNERABLE | 14.3.2 |
| object-path | 0.11.4 | 3 | VULNERABLE | 0.11.8 |
| qs | 6.5.0 | 3 | VULNERABLE | 6.16.0 |
| ws | 7.0.0 | 3 | VULNERABLE | 8.22.0 |
| ajv | 6.10.0 | 2 | VULNERABLE | 8.20.0 |
| body-parser | 1.18.0 | 2 | VULNERABLE | 1.20.8 |
| braces | 3.0.2 | 2 | VULNERABLE | none |
| dot | 1.1.2 | 2 | VULNERABLE | 2.0.0-beta.1 (prerelease only) |
| ejs | 2.7.4 | 2 | VULNERABLE | 6.0.1 |
| engine.io | 3.4.0 | 2 | VULNERABLE | 6.6.11 |
| express | 4.16.0 | 2 | VULNERABLE | 4.22.3 |
| express-fileupload | 1.1.6 | 2 | VULNERABLE | 1.5.2 |
| form-data | 2.5.0 | 2 | VULNERABLE | 2.5.6 |
| highlight.js | 9.15.9 | 2 | VULNERABLE | 11.12.0 |
| hoek | 4.2.0 | 2 | VULNERABLE | none |
| http-proxy-middleware | 0.20.0 | 2 | VULNERABLE | 4.2.0 |
| ip | 1.1.5 | 2 | VULNERABLE | none |
| jquery | 3.4.0 | 2 | VULNERABLE | 4.0.0 |
| karma | 4.4.0 | 2 | VULNERABLE | 6.4.4 |
| minimist | 1.2.0 | 2 | VULNERABLE | 1.2.8 |
| moment | 2.29.1 | 2 | VULNERABLE | 2.31.0 |
| node-fetch | 2.6.0 | 2 | VULNERABLE | 2.7.0 |
| path-to-regexp | 0.1.7 | 2 | VULNERABLE | 8.4.2 |
| pug | 2.0.4 | 2 | VULNERABLE | 3.0.4 |
| serialize-javascript | 2.1.0 | 2 | VULNERABLE | 7.1.2 |
| set-value | 2.0.0 | 2 | VULNERABLE | 3.0.3 |
| shelljs | 0.8.3 | 2 | VULNERABLE | 0.10.0 |
| socket.io | 2.3.0 | 2 | VULNERABLE | 4.8.4 |
| underscore | 1.12.0 | 2 | VULNERABLE | 1.13.8 |
| validator | 10.11.0 | 2 | VULNERABLE | 13.15.35 |
| yarn | 1.22.0 | 2 | VULNERABLE | 2.4.3 |
| acorn | 6.0.0 | 1 | VULNERABLE | 8.18.0 |
| ansi-regex | 5.0.0 | 1 | VULNERABLE | 6.4.0 |
| async | 2.6.0 | 1 | VULNERABLE | 3.2.6 |
| cookie | 0.4.0 | 1 | VULNERABLE | 2.0.1 |
| cross-spawn | 6.0.5 | 1 | VULNERABLE | 6.0.6 |
| debug | 4.1.0 | 1 | VULNERABLE | 4.4.3 |
| dot-prop | 4.2.0 | 1 | VULNERABLE | 10.2.0 |
| flat | 4.1.0 | 1 | VULNERABLE | 6.0.1 |
| glob-parent | 5.1.0 | 1 | VULNERABLE | 6.0.2 |
| got | 9.6.0 | 1 | VULNERABLE | 16.0.0 |
| http-proxy | 1.18.0 | 1 | VULNERABLE | 1.18.1 |
| ini | 1.3.5 | 1 | VULNERABLE | 7.0.0 |
| jws | 3.2.2 | 1 | VULNERABLE | 4.0.1 |
| kind-of | 6.0.2 | 1 | VULNERABLE | 6.0.3 |
| lodash.merge | 4.6.1 | 1 | VULNERABLE | 4.6.2 |
| lodash.set | 4.3.2 | 1 | VULNERABLE | none |
| lodash.template | 4.4.0 | 1 | VULNERABLE | 4.18.1 |
| marked | 0.7.0 | 1 | VULNERABLE | 18.0.14 |
| merge | 1.2.1 | 1 | VULNERABLE | 2.1.1 |
| micromatch | 4.0.2 | 1 | VULNERABLE | 4.0.8 |
| mixin-deep | 1.3.1 | 1 | VULNERABLE | 1.3.2 |
| mongodb | 3.5.0 | 1 | VULNERABLE | 7.7.0-dev (prerelease only) |
| mysql | 2.17.0 | 1 | VULNERABLE | 2.18.1 |
| node-jose | 1.1.3 | 1 | VULNERABLE | 2.2.0 |
| node-notifier | 5.4.0 | 1 | VULNERABLE | 10.0.1 |
| nunjucks | 3.2.0 | 1 | VULNERABLE | 3.2.4 |
| passport | 0.4.0 | 1 | VULNERABLE | 0.7.0 |
| redis | 3.0.0 | 1 | VULNERABLE | 6.3.0 |
| request | 2.88.0 | 1 | VULNERABLE | none |
| rollup | 1.27.0 | 1 | VULNERABLE | 4.64.0 |
| semver | 5.7.0 | 1 | VULNERABLE | 7.8.5 |
| send | 0.17.1 | 1 | VULNERABLE | 1.2.1 |
| serve-static | 1.14.1 | 1 | VULNERABLE | 2.2.1 |
| sockjs | 0.3.19 | 1 | VULNERABLE | 0.3.24 |
| terser | 4.4.0 | 1 | VULNERABLE | 5.51.2 |
| tmp | 0.1.0 | 1 | VULNERABLE | 0.2.7 |
| tough-cookie | 2.5.0 | 1 | VULNERABLE | 6.0.2 |
| trim-newlines | 3.0.0 | 1 | VULNERABLE | 5.0.0 |
| ua-parser-js | 0.7.28 | 1 | VULNERABLE | 2.0.10 |
| urllib | 2.34.0 | 1 | VULNERABLE | 2.44.1 |
| uuid | 3.3.2 | 1 | VULNERABLE | 14.0.2 |
| vue | 2.6.10 | 1 | VULNERABLE | 3.6.0-rc.10 (prerelease only) |
| xml2js | 0.4.19 | 1 | VULNERABLE | 0.6.2 |
| y18n | 4.0.0 | 1 | VULNERABLE | 5.0.8 |
| yaml | 1.7.0 | 1 | VULNERABLE | 3.0.0-2 (prerelease only) |

## Clean (94)

| Package | Version | Advisories | Verdict | Note |
|---|---|---|---|---|
| accepts | 1.3.7 | 0 | CLEAN | No known vulnerabilities or malware |
| ava | 2.4.0 | 0 | CLEAN | No known vulnerabilities or malware |
| babel-loader | 8.0.6 | 0 | CLEAN | No known vulnerabilities or malware |
| bcryptjs | 2.4.3 | 0 | CLEAN | No known vulnerabilities or malware |
| bluebird | 3.5.0 | 0 | CLEAN | No known vulnerabilities or malware |
| bower | 1.8.8 | 0 | CLEAN | No known vulnerabilities or malware |
| browserify | 16.5.0 | 0 | CLEAN | No known vulnerabilities or malware |
| chai | 4.2.0 | 0 | CLEAN | No known vulnerabilities or malware |
| chalk | 4.1.2 | 0 | CLEAN | No known vulnerabilities or malware |
| cheerio | 1.0.0-rc.3 | 0 | CLEAN | No known vulnerabilities or malware |
| chokidar | 3.3.0 | 0 | CLEAN | No known vulnerabilities or malware |
| classnames | 2.2.6 | 0 | CLEAN | No known vulnerabilities or malware |
| clean-css | 4.2.1 | 0 | CLEAN | No known vulnerabilities or malware |
| color-name | 1.1.4 | 0 | CLEAN | No known vulnerabilities or malware |
| colors | 1.4.0 | 0 | CLEAN | No known vulnerabilities or malware |
| commander | 2.20.0 | 0 | CLEAN | No known vulnerabilities or malware |
| content-type | 1.0.4 | 0 | CLEAN | No known vulnerabilities or malware |
| cookie-parser | 1.4.0 | 0 | CLEAN | No known vulnerabilities or malware |
| core-js | 2.6.11 | 0 | CLEAN | No known vulnerabilities or malware |
| cors | 2.8.5 | 0 | CLEAN | No known vulnerabilities or malware |
| css-loader | 3.2.0 | 0 | CLEAN | No known vulnerabilities or malware |
| date-fns | 2.8.0 | 0 | CLEAN | No known vulnerabilities or malware |
| dayjs | 1.8.0 | 0 | CLEAN | No known vulnerabilities or malware |
| deep-extend | 0.5.1 | 0 | CLEAN | No known vulnerabilities or malware |
| depd | 1.1.2 | 0 | CLEAN | No known vulnerabilities or malware |
| dotenv | 8.2.0 | 0 | CLEAN | No known vulnerabilities or malware |
| eslint | 6.8.0 | 0 | CLEAN | No known vulnerabilities or malware |
| execa | 3.4.0 | 0 | CLEAN | No known vulnerabilities or malware |
| express-session | 1.15.0 | 0 | CLEAN | No known vulnerabilities or malware |
| express-validator | 6.4.0 | 0 | CLEAN | No known vulnerabilities or malware |
| extend | 3.0.2 | 0 | CLEAN | No known vulnerabilities or malware |
| faker | 5.5.3 | 0 | CLEAN | No known vulnerabilities or malware |
| file-loader | 4.3.0 | 0 | CLEAN | No known vulnerabilities or malware |
| finalhandler | 1.1.2 | 0 | CLEAN | No known vulnerabilities or malware |
| fs-extra | 8.1.0 | 0 | CLEAN | No known vulnerabilities or malware |
| glob | 7.1.0 | 0 | CLEAN | No known vulnerabilities or malware |
| gulp | 4.0.0 | 0 | CLEAN | No known vulnerabilities or malware |
| helmet | 3.21.0 | 0 | CLEAN | No known vulnerabilities or malware |
| history | 4.10.1 | 0 | CLEAN | No known vulnerabilities or malware |
| html-webpack-plugin | 3.2.0 | 0 | CLEAN | No known vulnerabilities or malware |
| http-errors | 1.7.2 | 0 | CLEAN | No known vulnerabilities or malware |
| is-number | 7.0.0 | 0 | CLEAN | No known vulnerabilities or malware |
| is-promise | 2.1.0 | 0 | CLEAN | No known vulnerabilities or malware |
| jasmine | 3.5.0 | 0 | CLEAN | No known vulnerabilities or malware |
| jest | 25.1.0 | 0 | CLEAN | No known vulnerabilities or malware |
| js-beautify | 1.10.0 | 0 | CLEAN | No known vulnerabilities or malware |
| left-pad | 1.3.0 | 0 | CLEAN | No known vulnerabilities or malware |
| less | 3.10.0 | 0 | CLEAN | No known vulnerabilities or malware |
| lodash.get | 4.4.2 | 0 | CLEAN | No known vulnerabilities or malware |
| lru-cache | 5.1.1 | 0 | CLEAN | No known vulnerabilities or malware |
| mime | 2.4.4 | 0 | CLEAN | No known vulnerabilities or malware |
| mkdirp | 0.5.1 | 0 | CLEAN | No known vulnerabilities or malware |
| mocha | 6.2.0 | 0 | CLEAN | No known vulnerabilities or malware |
| ms | 2.1.2 | 0 | CLEAN | No known vulnerabilities or malware |
| mustache | 3.0.0 | 0 | CLEAN | No known vulnerabilities or malware |
| needle | 2.4.0 | 0 | CLEAN | No known vulnerabilities or malware |
| nock | 11.7.0 | 0 | CLEAN | No known vulnerabilities or malware |
| nodemon | 1.19.0 | 0 | CLEAN | No known vulnerabilities or malware |
| oauth | 0.9.15 | 0 | CLEAN | No known vulnerabilities or malware |
| passport-jwt | 4.0.0 | 0 | CLEAN | No known vulnerabilities or malware |
| passport-local | 1.0.0 | 0 | CLEAN | No known vulnerabilities or malware |
| pg | 8.0.0 | 0 | CLEAN | No known vulnerabilities or malware |
| prettier | 1.19.1 | 0 | CLEAN | No known vulnerabilities or malware |
| prop-types | 15.7.2 | 0 | CLEAN | No known vulnerabilities or malware |
| protractor | 5.4.2 | 0 | CLEAN | No known vulnerabilities or malware |
| ramda | 0.27.0 | 0 | CLEAN | No known vulnerabilities or malware |
| react | 16.13.0 | 0 | CLEAN | No known vulnerabilities or malware |
| react-dom | 16.13.0 | 0 | CLEAN | No known vulnerabilities or malware |
| readable-stream | 3.4.0 | 0 | CLEAN | No known vulnerabilities or malware |
| redux | 4.0.5 | 0 | CLEAN | No known vulnerabilities or malware |
| request-promise | 4.2.5 | 0 | CLEAN | No known vulnerabilities or malware |
| rimraf | 2.7.1 | 0 | CLEAN | No known vulnerabilities or malware |
| rxjs | 6.5.0 | 0 | CLEAN | No known vulnerabilities or malware |
| safe-buffer | 5.1.2 | 0 | CLEAN | No known vulnerabilities or malware |
| sass | 1.23.0 | 0 | CLEAN | No known vulnerabilities or malware |
| sinon | 7.5.0 | 0 | CLEAN | No known vulnerabilities or malware |
| socket.io-client | 2.3.0 | 0 | CLEAN | No known vulnerabilities or malware |
| strip-ansi | 6.0.0 | 0 | CLEAN | No known vulnerabilities or malware |
| style-loader | 1.0.0 | 0 | CLEAN | No known vulnerabilities or malware |
| styled-components | 5.0.0 | 0 | CLEAN | No known vulnerabilities or malware |
| stylelint | 12.0.0 | 0 | CLEAN | No known vulnerabilities or malware |
| superagent | 5.2.0 | 0 | CLEAN | No known vulnerabilities or malware |
| supertest | 4.0.2 | 0 | CLEAN | No known vulnerabilities or malware |
| tape | 4.11.0 | 0 | CLEAN | No known vulnerabilities or malware |
| through2 | 3.0.1 | 0 | CLEAN | No known vulnerabilities or malware |
| tslib | 1.10.0 | 0 | CLEAN | No known vulnerabilities or malware |
| typescript | 3.7.2 | 0 | CLEAN | No known vulnerabilities or malware |
| uglify-js | 3.7.0 | 0 | CLEAN | No known vulnerabilities or malware |
| url-loader | 2.2.0 | 0 | CLEAN | No known vulnerabilities or malware |
| vue-router | 3.1.0 | 0 | CLEAN | No known vulnerabilities or malware |
| webpack | 4.41.0 | 0 | CLEAN | No known vulnerabilities or malware |
| webpack-dev-middleware | 3.7.2 | 0 | CLEAN | No known vulnerabilities or malware |
| xss | 1.0.8 | 0 | CLEAN | No known vulnerabilities or malware |
| yargs | 15.0.0 | 0 | CLEAN | No known vulnerabilities or malware |
