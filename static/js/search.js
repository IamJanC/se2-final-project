document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('searchInput');      // matches your HTML
  const suggestionsBox = document.getElementById('suggestionsBox'); // matches your HTML

  if (!searchInput || !suggestionsBox) return; // safety

  // Simple debounce
  function debounce(fn, wait = 180) {
    let t;
    return function (...args) {
      clearTimeout(t);
      t = setTimeout(() => fn.apply(this, args), wait);
    };
  }

  async function fetchSuggestions(q) {
    if (!q || q.length < 1) {
      suggestionsBox.innerHTML = '';
      suggestionsBox.style.display = 'none';
      return;
    }

    try {
      const res = await fetch(`/products/search/?q=${encodeURIComponent(q)}`);
      if (!res.ok) throw new Error('Network error');
      const data = await res.json();

      suggestionsBox.innerHTML = '';

      if (!data || data.length === 0) {
        const no = document.createElement('div');
        no.className = 'no-results';
        no.textContent = 'No matching products.';
        suggestionsBox.appendChild(no);
        suggestionsBox.style.display = 'block';
        return;
      }

      data.forEach(item => {
        const a = document.createElement('a');
        a.className = 'suggestion-item';
        a.href = item.url || (`/shop/${item.id}/`); // use returned url, fallback to /shop/id
        a.innerHTML = `
            <div class="s-right">
            <div class="s-name">${item.name}</div>
            ${item.price ? `<div class="s-price">₱${item.price}</div>` : ''}
            </div>
        `;
        suggestionsBox.appendChild(a);
        });

      suggestionsBox.style.display = 'block';
    } catch (err) {
      console.error('Search error', err);
      suggestionsBox.innerHTML = '';
      suggestionsBox.style.display = 'none';
    }
  }

  const debounced = debounce((e) => fetchSuggestions(e.target.value), 180);
  searchInput.addEventListener('input', debounced);

  // Hide suggestions when clicking outside
  document.addEventListener('click', (ev) => {
    if (!ev.target.closest('.search-bar')) {
      suggestionsBox.innerHTML = '';
      suggestionsBox.style.display = 'none';
    }
  });
});

