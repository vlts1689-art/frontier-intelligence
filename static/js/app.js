document.addEventListener('DOMContentLoaded', () => {
  const cards = document.querySelectorAll('.panel-card');
  cards.forEach((card, index) => {
    card.style.animationDelay = `${index * 80}ms`;
    card.classList.add('fade-in');
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
