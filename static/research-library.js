(() => {
  const query = document.querySelector("#library-query");
  const area = document.querySelector("#library-area");
  const year = document.querySelector("#library-year");
  const kind = document.querySelector("#library-kind");
  const status = document.querySelector("#library-status");
  const clear = document.querySelector("#library-clear");
  const count = document.querySelector("#library-count");
  const empty = document.querySelector("#library-empty");
  const entries = [...document.querySelectorAll(".library-entry")];
  const groups = [...document.querySelectorAll(".library-year-group")];

  if (!query || !area || !year || !kind || !status || !clear || !count || !empty) return;

  function applyFilters() {
    const search = query.value.trim().toLowerCase();
    let visible = 0;

    entries.forEach((entry) => {
      const entryAreas = entry.dataset.areas.toLowerCase().split("|");
      const searchable = [
        entry.dataset.title,
        entry.dataset.venue,
        entry.dataset.areas,
        entry.dataset.org,
        entry.dataset.contact,
      ].join(" ").toLowerCase();
      const matches =
        (!search || searchable.includes(search)) &&
        (!area.value || entryAreas.includes(area.value)) &&
        (!year.value || entry.dataset.year === year.value) &&
        (!kind.value || entry.dataset.kind.toLowerCase() === kind.value) &&
        (!status.value || entry.dataset.status.toLowerCase() === status.value);
      entry.hidden = !matches;
      if (matches) visible += 1;
    });

    groups.forEach((group) => {
      group.hidden = !group.querySelector(".library-entry:not([hidden])");
    });
    count.textContent = visible;
    empty.hidden = visible !== 0;
  }

  [query, area, year, kind, status].forEach((control) => {
    control.addEventListener(control === query ? "input" : "change", applyFilters);
  });

  clear.addEventListener("click", () => {
    query.value = "";
    area.value = "";
    year.value = "";
    kind.value = "";
    status.value = "";
    applyFilters();
    query.focus();
  });
})();
