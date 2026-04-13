import { optionalApiKey, fetchApi, formatModel, parseArgs } from "./lib.js";

const apiKey = optionalApiKey();
const args = parseArgs(process.argv.slice(2));
const query = args.get("_0") as string | undefined;
const modality = args.get("modality") as string | undefined;
const sort = args.get("sort") as string | undefined;

const json = await fetchApi("/models", apiKey);
let models: any[] = json.data ?? [];

// Filter to only free models: both prompt and completion must be "0"
models = models.filter((m: any) => {
  const prompt = m.pricing?.prompt;
  const completion = m.pricing?.completion;
  return (
    (prompt === "0" || parseFloat(prompt ?? "1") === 0) &&
    (completion === "0" || parseFloat(completion ?? "1") === 0)
  );
});

// Optional text query filter (name, id, description)
if (query) {
  const lowerQuery = query.toLowerCase();
  models = models.filter((m: any) => {
    const id = (m.id ?? "").toLowerCase();
    const name = (m.name ?? "").toLowerCase();
    const desc = (m.description ?? "").toLowerCase();
    return id.includes(lowerQuery) || name.includes(lowerQuery) || desc.includes(lowerQuery);
  });
}

// Optional modality filter
if (modality) {
  const lowerModality = modality.toLowerCase();
  models = models.filter((m: any) => {
    const inputMods: string[] = m.architecture?.input_modalities ?? [];
    const outputMods: string[] = m.architecture?.output_modalities ?? [];
    return [...inputMods, ...outputMods]
      .map((mod: string) => mod.toLowerCase())
      .includes(lowerModality);
  });
}

// Sort
if (sort === "context") {
  models.sort((a: any, b: any) => (b.context_length ?? 0) - (a.context_length ?? 0));
} else if (sort === "newest") {
  models.sort((a: any, b: any) => (b.created ?? 0) - (a.created ?? 0));
} else if (sort === "throughput" || sort === "speed") {
  models.sort(
    (a: any, b: any) =>
      (b.top_provider?.max_completion_tokens ?? 0) - (a.top_provider?.max_completion_tokens ?? 0)
  );
}

if (models.length === 0) {
  console.error(
    query || modality
      ? `No free models found matching your criteria.`
      : `No free models found.`
  );
  console.log(JSON.stringify([], null, 2));
  process.exit(0);
}

// Format output with extra "best_for" field derived from description
const output = models.map((m: any) => {
  const formatted = formatModel(m);
  return {
    ...formatted,
    is_free: true,
    modality: m.architecture?.modality ?? null,
    input_modalities: m.architecture?.input_modalities ?? [],
    output_modalities: m.architecture?.output_modalities ?? [],
  };
});

console.log(JSON.stringify(output, null, 2));
