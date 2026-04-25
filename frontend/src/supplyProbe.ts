export async function probeOptionalDependency(moduleName: string): Promise<string> {
  const target = (moduleName || "").trim();
  if (!target) return "missing module name";
  try {
    const dynImport = new Function("m", "return import(m)") as (m: string) => Promise<unknown>;
    const mod = await dynImport(target);
    return `imported: ${target} (${Object.keys((mod as Record<string, unknown>) || {}).length} exports)`;
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    return `import-error: ${target} (${msg})`;
  }
}
