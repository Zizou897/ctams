(function () {
  var list = document.getElementById('partners-list');
  var status = document.getElementById('partners-status');

  if (!list || !status) {
    return;
  }

  function showMessage(message, isError) {
    status.textContent = message;
    status.classList.remove('hidden');
    status.setAttribute('role', isError ? 'alert' : 'status');
    list.replaceChildren(status);
  }

  function safeHttpUrl(value) {
    if (typeof value !== 'string' || !value.trim()) {
      return '';
    }

    try {
      var url = new URL(value, window.location.href);
      return url.protocol === 'https:' || url.protocol === 'http:' ? url.href : '';
    } catch (error) {
      return '';
    }
  }

  function createPartner(partner) {
    if (!partner || typeof partner.name !== 'string' || !partner.name.trim()) {
      return null;
    }

    var item = document.createElement('article');
    item.className = 'flex w-full max-w-xs items-center justify-center rounded-xl border border-neutral-200 bg-white px-5 py-6 text-center';

    var logoUrl = safeHttpUrl(partner.logo_url || partner.logo);
    if (!logoUrl) {
      return null;
    }

    var logo = document.createElement('img');
    logo.src = logoUrl;
    logo.alt = partner.name;
    logo.width = 160;
    logo.height = 64;
    logo.loading = 'lazy';
    logo.className = 'h-14 max-w-full object-contain';
    logo.addEventListener('error', function () {
      item.remove();
    }, { once: true });
    item.appendChild(logo);
    return item;
  }

  var apiUrl = list.dataset.apiUrl;
  if (!apiUrl) {
    showMessage('Les partenaires seront affichés ici prochainement.', false);
    return;
  }

  var controller = new AbortController();
  var timeout = window.setTimeout(function () {
    controller.abort();
  }, 10000);

  fetch(apiUrl, {
    headers: { Accept: 'application/json' },
    credentials: 'omit',
    signal: controller.signal
  })
    .then(function (response) {
      if (!response.ok) {
        throw new Error('Partners API returned ' + response.status);
      }
      return response.json();
    })
    .then(function (data) {
      var partnerData = data && Array.isArray(data.partners)
        ? data.partners
        : data && typeof data.name === 'string'
          ? [data]
          : null;

      if (!partnerData) {
        throw new Error('Partners API returned an invalid response');
      }

      var partners = partnerData.map(createPartner).filter(Boolean);
      if (!partners.length) {
        showMessage('Aucun partenaire à afficher pour le moment.', false);
        return;
      }

      list.replaceChildren.apply(list, partners);
    })
    .catch(function () {
      showMessage('Les partenaires ne sont pas disponibles pour le moment.', true);
    })
    .finally(function () {
      window.clearTimeout(timeout);
    });
})();
