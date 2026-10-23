(function () {
  var root = document.documentElement;

  // ---- theme toggle (remembers choice when storage is available) ----
  var btn = document.getElementById('theme-btn');
  function currentTheme() {
    var t = root.getAttribute('data-theme');
    if (t) return t;
    return window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  if (btn) {
    btn.addEventListener('click', function () {
      var next = currentTheme() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (e) {}
      btn.setAttribute('aria-label', next === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
    });
  }

  // ---- mobile menu ----
  var toggle = document.getElementById('nav-toggle');
  var nav = document.getElementById('nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.textContent = open ? 'Close' : 'Menu';
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a') && nav.classList.contains('open')) toggle.click();
    });
  }

  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  // ---- copy email ----
  document.querySelectorAll('.copy').forEach(function (b) {
    b.addEventListener('click', function () {
      var text = b.getAttribute('data-copy');
      var done = function () { b.textContent = 'Copied'; setTimeout(function () { b.textContent = 'Copy'; }, 1600); };
      try { navigator.clipboard.writeText(text).then(done, function () { b.textContent = text; }); }
      catch (e) { b.textContent = text; }
    });
  });

  // ---- reveal on scroll ----
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    document.querySelectorAll('.reveal').forEach(function (el) { io.observe(el); });
  } else {
    document.querySelectorAll('.reveal').forEach(function (el) { el.classList.add('in'); });
  }

  // ---- field-notes filters ----
  var notes = Array.prototype.slice.call(document.querySelectorAll('.note'));
  document.querySelectorAll('.filters button').forEach(function (b, _, all) {
    b.addEventListener('click', function () {
      var f = b.getAttribute('data-filter');
      all.forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
      notes.forEach(function (n) {
        n.hidden = !(f === 'all' || (' ' + n.getAttribute('data-tags') + ' ').indexOf(' ' + f + ' ') > -1);
      });
    });
  });

  // ---- lightbox with prev / next ----
  var box = document.getElementById('lightbox');
  if (box && typeof box.showModal === 'function') {
    var img = document.getElementById('lightbox-img');
    var cap = document.getElementById('lightbox-cap');
    var idx = 0;
    function visible() { return notes.filter(function (n) { return !n.hidden; }); }
    function show(i) {
      var list = visible(); if (!list.length) return;
      idx = (i + list.length) % list.length;
      var fig = list[idx], t = fig.querySelector('img');
      img.src = t.getAttribute('data-full') || t.currentSrc || t.src;
      img.alt = t.alt;
      cap.textContent = fig.querySelector('.what').textContent + ' · ' + fig.querySelector('.date').textContent;
    }
    notes.forEach(function (n) {
      n.querySelector('button').addEventListener('click', function () {
        show(visible().indexOf(n));
        box.showModal();
      });
    });
    document.getElementById('lightbox-close').addEventListener('click', function () { box.close(); });
    document.getElementById('lightbox-prev').addEventListener('click', function () { show(idx - 1); });
    document.getElementById('lightbox-next').addEventListener('click', function () { show(idx + 1); });
    box.addEventListener('click', function (e) { if (e.target === box || e.target.classList.contains('stage')) box.close(); });
    box.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') show(idx - 1);
      if (e.key === 'ArrowRight') show(idx + 1);
    });
  }

  // ---- contact form (FormSubmit; falls back to an email draft) ----
  var form = document.getElementById('contact-form');
  if (form) {
    var status = form.querySelector('.status');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (form.querySelector('[name="_honey"]').value) return;
      var data = {};
      new FormData(form).forEach(function (v, k) { data[k] = v; });
      data._subject = 'Website: ' + (data.topic || 'Hello') + ' from ' + (data.name || 'someone');
      data._template = 'table';
      var submit = form.querySelector('button[type="submit"]');
      submit.disabled = true; status.className = 'status'; status.textContent = 'Sending…';
      fetch(form.getAttribute('action'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(data)
      }).then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          if (res.ok && String(res.j.success) !== 'false') {
            form.reset(); status.className = 'status ok';
            status.textContent = 'Thanks, your message is on its way. I usually reply within a couple of days.';
          } else { throw new Error('send failed'); }
        })
        .catch(function () {
          status.className = 'status err';
          var body = encodeURIComponent((data.message || '') + '\n\n— ' + (data.name || '') + (data.org ? ', ' + data.org : ''));
          status.innerHTML = 'That didn’t go through. <a href="mailto:drew.reeve@gmail.com?subject=' + encodeURIComponent(data._subject) + '&body=' + body + '">Send it by email instead</a>.';
        })
        .then(function () { submit.disabled = false; });
    });
  }
})();
