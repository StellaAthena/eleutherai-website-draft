(() => {
  const query = document.querySelector("#library-query");
  const area = document.querySelector("#library-area");
  const year = document.querySelector("#library-year");
  const kind = document.querySelector("#library-kind");
  const venue = document.querySelector("#library-venue");
  const clear = document.querySelector("#library-clear");
  const emptyClear = document.querySelector("#library-empty-clear");
  const count = document.querySelector("#library-count");
  const empty = document.querySelector("#library-empty");
  const filterStatus = document.querySelector("#library-filter-status");
  const entries = [...document.querySelectorAll(".library-entry")];
  const groups = [...document.querySelectorAll(".library-year-group")];

  if (!query || !area || !year || !kind || !venue || !clear || !emptyClear || !count || !empty || !filterStatus) return;

  const areaLabels = new Map([...area.options].slice(1).map((option) => [option.value, option.textContent]));

  const yearLabels = new Map([...year.options].slice(1).map((option) => [option.value, option.textContent]));
  const kindLabels = new Map([...kind.options].slice(1).map((option) => [option.value, option.textContent]));
  const venueLabels = new Map([...venue.options].slice(1).map((option) => [option.value, option.textContent]));

  function countsFor(items, key) {
    return items.reduce((counts, entry) => {
      const value = entry.dataset[key];
      if (value) counts.set(value, (counts.get(value) || 0) + 1);
      return counts;
    }, new Map());
  }

  function setOptionCounts(select, labels, counts) {
    [...select.options].slice(1).forEach((option) => {
      option.textContent = `${labels.get(option.value) || option.value} (${counts.get(option.value) || 0})`;
    });
  }

  function rebuildOptions(select, allLabel, labels, counts) {
    const selected = select.value;
    const options = document.createDocumentFragment();
    options.append(new Option(allLabel, ""));

    [...labels]
      .filter(([value]) => counts.has(value))
      .forEach(([value, label]) => options.append(new Option(`${label} (${counts.get(value)})`, value)));

    select.replaceChildren(options);
    const selectionRemainsAvailable = !selected || counts.has(selected);
    select.value = selectionRemainsAvailable ? selected : "";
    return Boolean(selected) && !selectionRemainsAvailable;
  }

  function compactKindLabels(labels) {
    return new Map([...labels].map(([value, label]) => [
      value,
      value === "conference" ? "Conference / journal" : label,
    ]));
  }

  function entryAreas(entry) {
    return (entry.dataset.areas || "").split("|").filter(Boolean);
  }

  function areaCounts(items) {
    return items.reduce((counts, entry) => {
      entryAreas(entry).forEach((value) => counts.set(value, (counts.get(value) || 0) + 1));
      return counts;
    }, new Map());
  }

  function updateDependentFilters() {
    const areaEntries = entries.filter((entry) => !area.value || entryAreas(entry).includes(area.value));
    const yearEntries = areaEntries.filter((entry) => !year.value || entry.dataset.year === year.value);
    const kindReset = rebuildOptions(kind, "All venue types", compactKindLabels(kindLabels), countsFor(yearEntries, "kind"));
    const kindEntries = yearEntries.filter((entry) => !kind.value || entry.dataset.kind === kind.value);
    const venueReset = rebuildOptions(venue, "All venues", venueLabels, countsFor(kindEntries, "family"));

    const resetLabels = [];
    if (kindReset) resetLabels.push("venue type");
    if (venueReset) resetLabels.push("venue");
    filterStatus.textContent = resetLabels.length
      ? `${resetLabels.join(" and ")} reset because the selection is not available for the current filters.`
      : "";
  }

  function applyFilters() {
    const search = query.value.trim().toLowerCase();
    let visible = 0;

    entries.forEach((entry) => {
      const searchable = [
        entry.dataset.title,
        entry.dataset.authors,
        entry.dataset.venue,
        entry.dataset.areas,
        entry.dataset.org,
        entry.dataset.contact,
      ].join(" ").toLowerCase();
      const matches =
        (!search || searchable.includes(search)) &&
        (!area.value || entryAreas(entry).includes(area.value)) &&
        (!year.value || entry.dataset.year === year.value) &&
        (!kind.value || entry.dataset.kind.toLowerCase() === kind.value) &&
        (!venue.value || entry.dataset.family.toLowerCase() === venue.value);
      entry.hidden = !matches;
      if (matches) visible += 1;
    });

    groups.forEach((group) => {
      group.hidden = !group.querySelector(".library-entry:not([hidden])");
    });
    count.textContent = visible;
    empty.hidden = visible !== 0;
  }

  query.addEventListener("input", applyFilters);
  area.addEventListener("change", () => {
    setOptionCounts(year, yearLabels, countsFor(entries.filter((entry) => !area.value || entryAreas(entry).includes(area.value)), "year"));
    updateDependentFilters();
    applyFilters();
  });
  year.addEventListener("change", () => {
    updateDependentFilters();
    applyFilters();
  });
  kind.addEventListener("change", () => {
    updateDependentFilters();
    applyFilters();
  });
  venue.addEventListener("change", applyFilters);

  function clearFilters() {
    query.value = "";
    area.value = "";
    setOptionCounts(year, yearLabels, countsFor(entries, "year"));
    year.value = "";
    kind.value = "";
    venue.value = "";
    updateDependentFilters();
    applyFilters();
    query.focus();
  }

  clear.addEventListener("click", clearFilters);
  emptyClear.addEventListener("click", clearFilters);

  setOptionCounts(area, areaLabels, areaCounts(entries));
  setOptionCounts(year, yearLabels, countsFor(entries, "year"));

  // Deep links from research-area pages: /papers/?area=Open-Weight%20Safety
  const params = new URLSearchParams(window.location.search);
  const requestedArea = (params.get("area") || "").trim().toLowerCase();
  if (requestedArea && areaLabels.has(requestedArea)) {
    area.value = requestedArea;
    setOptionCounts(year, yearLabels, countsFor(entries.filter((entry) => entryAreas(entry).includes(requestedArea)), "year"));
  }
  const requestedQuery = (params.get("q") || "").trim();
  if (requestedQuery) query.value = requestedQuery;

  updateDependentFilters();
  applyFilters();
})();
