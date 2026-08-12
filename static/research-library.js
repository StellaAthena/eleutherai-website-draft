(() => {
  const query = document.querySelector("#library-query");
  const year = document.querySelector("#library-year");
  const kind = document.querySelector("#library-kind");
  const venue = document.querySelector("#library-venue");
  const clear = document.querySelector("#library-clear");
  const count = document.querySelector("#library-count");
  const empty = document.querySelector("#library-empty");
  const entries = [...document.querySelectorAll(".library-entry")];
  const groups = [...document.querySelectorAll(".library-year-group")];

  if (!query || !year || !kind || !venue || !clear || !count || !empty) return;

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

  [query, year, kind, venue].forEach((control) => {
    control.addEventListener(control === query ? "input" : "change", applyFilters);
  });

  clear.addEventListener("click", () => {
    query.value = "";
    year.value = "";
    kind.value = "";
    venue.value = "";
    applyFilters();
    query.focus();
  });
})();
