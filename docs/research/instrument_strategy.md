# Instrument Strategy

## Asset Class Versus Instrument

An entity gets a primary asset class based on its main role in the industry atlas:

- capital provider,
- acquirer,
- studio,
- search/ETA platform,
- sovereign allocator,
- marketplace,
- capital or instrument provider.

An instrument describes the financing mechanism or economic structure the entity uses:

- revenue share,
- revenue-based financing,
- shared earnings,
- royalties,
- capped returns,
- non-dilutive capital,
- growth debt,
- search capital,
- permanent equity,
- studio equity,
- acquisition marketplace.

The same entity can have one asset-class bucket and several instruments.

`Instrument` is not a valid primary asset class for an entity. It is retained only as an instrument-family taxonomy row and as a secondary tag where useful.

## Mapping Rule

Map an instrument to an entity only when the entity's source language, product, or operating model makes the instrument relevant. Do not map generic equity to every investor. Generic equity is too broad unless it helps explain a specific post-unicorn structure.

Use `instrument_provider_map.csv` for the many-to-many relationship:

```text
instrument -> provider entity -> source URL -> evidence status
```

## Why Instrument Provider Exports Contain Companies

The shareable atlas packet separates entity asset-class sections from `Instrument Providers And Financing Mechanisms`. Capital providers and financing platforms should appear under a real entity bucket such as `SMV`, `LMV`, or `Patient Capital`, while their mechanisms are shown through `instrument_types` and `instrument_provider_map.csv`.

`instrument_provider_map.csv` is the more precise table for instrument relationships. It answers which provider is associated with revenue share, revenue-based financing, shared earnings, search capital, permanent equity, and similar mechanisms.

`funds_instruments.csv` is legacy supporting evidence retained for continuity until its rows are migrated into the atlas schema.

## TinySeed Example

TinySeed's primary bucket is `SMV` because it is infrastructure for bootstrapped B2B SaaS founders and non-unicorn company-building paths.

TinySeed is also mapped to `revenue_share` because its capital model is revenue-linked. That instrument helps explain why TinySeed is not just a normal accelerator row.

## Khazanah Nasional Example

Khazanah Nasional's primary bucket is `Sovereign Capital` because it is a sovereign wealth allocator.

It is not mapped to specialized instruments such as revenue share, shared earnings, or search capital because the current seed source does not support that. Its broad `equity` instrument is captured in `industry_entities.csv`, but it is not enough to create a specialized `instrument_provider_map.csv` row.

## Review Standard

Instrument mappings are seed-level until source text directly supports the mechanism. A paper-ready instrument claim needs:

- source URL,
- source-text snippet,
- instrument type,
- provider entity,
- evidence status,
- human review before publication.
