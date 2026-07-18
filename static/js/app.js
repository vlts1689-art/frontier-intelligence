document.addEventListener('DOMContentLoaded', () => {
  const cards = document.querySelectorAll('.panel-card');
  cards.forEach((card, index) => {
    card.style.animationDelay = `${index * 80}ms`;
    card.classList.add('fade-in');
  });

  const refreshButton = document.getElementById('refresh-news-btn');
  const refreshStatus = document.getElementById('refresh-news-status');
  const refreshSummary = document.getElementById('refresh-news-summary');
  let isRefreshing = false;

  if (refreshButton && refreshStatus && refreshSummary) {
    refreshButton.addEventListener('click', async () => {
      if (isRefreshing) {
        return;
      }

      isRefreshing = true;
      refreshButton.disabled = true;
      refreshButton.innerHTML = '<span class="me-2">⏳</span>更新中…';
      refreshStatus.textContent = '';
      refreshSummary.textContent = '';

      try {
        const response = await fetch('/refresh-news', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        });
        const payload = await response.json();

        if (!response.ok || !payload.success) {
          throw new Error(payload.error || '更新に失敗しました。');
        }

        const summary = [
          '更新完了',
          `取得 ${payload.result.fetched_count || 0} 件`,
          `新規 ${payload.result.saved_count || 0} 件`,
          `重複 ${payload.result.duplicate_count || 0} 件`,
          `失敗 ${payload.result.failed_count || 0} 件`,
        ].join('\n');
        refreshStatus.textContent = '更新しました';
        refreshSummary.innerHTML = summary.replace(/\n/g, '<br>');
        const updatedAt = payload.result.completed_at || new Date().toISOString();
        window.location.href = `/?updated_at=${encodeURIComponent(updatedAt)}`;
      } catch (error) {
        refreshStatus.textContent = error.message || '更新に失敗しました。';
        refreshSummary.textContent = '';
        refreshButton.disabled = false;
        refreshButton.innerHTML = '<span class="me-2">🔄</span>ニュースを更新';
        isRefreshing = false;
      }
    });
  }

  const themeTabs = document.querySelectorAll('.theme-tab');
  const newsCards = Array.from(document.querySelectorAll('[data-news-card]'));
  const newsCountPill = document.getElementById('news-count-pill');

  themeTabs.forEach((button) => {
    button.addEventListener('click', () => {
      themeTabs.forEach((tab) => tab.classList.remove('active'));
      button.classList.add('active');
      const selectedTheme = button.dataset.theme || 'all';

      let visibleCount = 0;
      newsCards.forEach((card) => {
        const matches = selectedTheme === 'all' || matchesTheme(card.dataset.theme, selectedTheme);
        card.style.display = matches ? '' : 'none';
        if (matches) {
          visibleCount += 1;
        }
      });

      if (newsCountPill) {
        newsCountPill.textContent = `${visibleCount}件`;
      }
    });
  });

  document.querySelectorAll('.generate-tweet-btn').forEach((button) => {
    button.addEventListener('click', () => {
      const result = button.parentElement?.nextElementSibling;
      const output = result?.querySelector('.tweet-output');
      if (!result || !output) {
        return;
      }

      const text = buildTweetText({
        title: button.dataset.title || '',
        summary: button.dataset.summary || '',
        topic: button.dataset.topic || '',
        companies: button.dataset.companies || '',
      });

      output.textContent = text;
      result.classList.remove('d-none');
      button.textContent = '再生成する';
    });
  });

  document.querySelectorAll('.copy-tweet-btn').forEach((button) => {
    button.addEventListener('click', async () => {
      const output = button.previousElementSibling;
      const text = output?.textContent?.trim();
      if (!text) {
        return;
      }

      try {
        await navigator.clipboard.writeText(text);
        button.textContent = 'コピー済み';
        window.setTimeout(() => {
          button.textContent = 'コピー';
        }, 1500);
      } catch (error) {
        button.textContent = 'コピー失敗';
        window.setTimeout(() => {
          button.textContent = 'コピー';
        }, 1500);
      }
    });
  });
});

function matchesTheme(themeValue, selectedTheme) {
  if (!themeValue || selectedTheme === 'all') {
    return selectedTheme === 'all';
  }

  const normalizedTheme = themeValue.toLowerCase();
  const normalizedSelection = selectedTheme.toLowerCase();

  if (normalizedSelection === '電力') {
    return normalizedTheme.includes('電力') || normalizedTheme.includes('power') || normalizedTheme.includes('送配電');
  }

  if (normalizedSelection === 'バッテリー') {
    return normalizedTheme.includes('battery') || normalizedTheme.includes('バッテリー');
  }

  if (normalizedSelection === '量子') {
    return normalizedTheme.includes('quantum') || normalizedTheme.includes('量子');
  }

  if (normalizedSelection === 'バイオ') {
    return normalizedTheme.includes('bio') || normalizedTheme.includes('バイオ');
  }

  if (normalizedSelection === 'フィジカルAI') {
    return normalizedTheme.includes('physical') || normalizedTheme.includes('フィジカル') || normalizedTheme.includes('robot');
  }

  if (normalizedSelection === '宇宙') {
    return normalizedTheme.includes('space') || normalizedTheme.includes('宇宙');
  }

  if (normalizedSelection === '核融合') {
    return normalizedTheme.includes('fusion') || normalizedTheme.includes('核融合');
  }

  return normalizedTheme.includes(normalizedSelection);
}

function buildTweetText({ title, summary, topic, companies }) {
  const topicText = sanitizeText(topic) || 'ニュース';
  const titleText = sanitizeText(title) || '最近の動き';
  const summaryText = sanitizeText(summary) || '市場の注目が集まっている';
  const companyText = sanitizeText(companies)
    ? sanitizeText(companies).split(',')[0].trim()
    : '関連日本株';
  const body = `${topicText}のニュースに反応。${titleText}は、投資家目線では${companyText}への影響に注目したい展開だ。プレイヤーとしても期待と警戒が同居しており、短期の空気感がかなり変わる。${summaryText}。あなたはどう思う？`;

  return enforceTweetLength(body);
}

function sanitizeText(value) {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

function enforceTweetLength(text) {
  const suffix = 'あなたはどう思う？';
  const maxLength = 140;
  const body = text.endsWith(suffix) ? text.slice(0, -suffix.length) : text;

  if (body.length + suffix.length <= maxLength) {
    return `${body}${suffix}`;
  }

  const available = maxLength - suffix.length - 1;
  return `${body.slice(0, available).trimEnd()}…${suffix}`;
}
