// Decap CMS GitHub OAuth bridge. Deploy as a Cloudflare Worker.
const CMS_ORIGIN = 'https://xhhbot.com';

function hex(bytes) {
  const values = new Uint8Array(bytes);
  crypto.getRandomValues(values);
  return Array.from(values, value => value.toString(16).padStart(2, '0')).join('');
}

function response(body, status = 200, headers = {}) {
  return new Response(body, {
    status,
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 'no-store',
      'X-Content-Type-Options': 'nosniff',
      ...headers,
    },
  });
}

function callbackPage(status, token = '') {
  const payload = JSON.stringify({ token }).replaceAll('<', '\\u003c');
  const message = `authorization:github:${status}:${payload}`;
  const safeMessage = JSON.stringify(message).replaceAll('<', '\\u003c');
  return response(`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>鳕烩烩登录</title><body><p>${status === 'success' ? '登录完成，正在返回管理后台…' : '登录失败，请关闭窗口重试。'}</p><script>
    if (window.opener) {
      const receiveMessage = event => {
        if (event.origin !== ${JSON.stringify(CMS_ORIGIN)}) return;
        window.opener.postMessage(${safeMessage}, ${JSON.stringify(CMS_ORIGIN)});
        window.removeEventListener('message', receiveMessage);
      };
      window.addEventListener('message', receiveMessage);
      window.opener.postMessage('authorizing:github', ${JSON.stringify(CMS_ORIGIN)});
    }
  </script></body></html>`, 200, {
    'Content-Type': 'text/html; charset=utf-8',
    'Content-Security-Policy': `default-src 'none'; script-src 'unsafe-inline'; style-src 'none'; base-uri 'none'; frame-ancestors 'none'`,
    'Referrer-Policy': 'no-referrer',
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method !== 'GET') return response('Method not allowed', 405);
    if (!env.GITHUB_CLIENT_ID || !env.GITHUB_CLIENT_SECRET) {
      return response('OAuth is not configured', 503);
    }
    const callback = `${url.origin}/callback`;
    if (url.pathname === '/auth') {
      if (url.searchParams.get('provider') !== 'github') return response('Invalid provider', 400);
      const state = hex(32);
      const authorize = new URL('https://github.com/login/oauth/authorize');
      authorize.searchParams.set('client_id', env.GITHUB_CLIENT_ID);
      authorize.searchParams.set('redirect_uri', callback);
      authorize.searchParams.set('scope', 'public_repo');
      authorize.searchParams.set('state', state);
      return response(null, 302, {
        Location: authorize.toString(),
        'Set-Cookie': `oauth_state=${state}; HttpOnly; Secure; SameSite=Lax; Path=/callback; Max-Age=600`,
      });
    }
    if (url.pathname === '/callback') {
      const state = url.searchParams.get('state');
      const cookie = request.headers.get('Cookie')?.match(/(?:^|;\s*)oauth_state=([a-f0-9]{64})(?:;|$)/)?.[1];
      if (!state || !cookie || state !== cookie) return response('Invalid OAuth state', 403);
      if (url.searchParams.has('error')) return callbackPage('error');
      const code = url.searchParams.get('code');
      if (!code) return response('Missing authorization code', 400);
      const tokenResponse = await fetch('https://github.com/login/oauth/access_token', {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({
          client_id: env.GITHUB_CLIENT_ID,
          client_secret: env.GITHUB_CLIENT_SECRET,
          code,
          redirect_uri: callback,
        }),
      });
      if (!tokenResponse.ok) return callbackPage('error');
      const result = await tokenResponse.json();
      if (!result.access_token) return callbackPage('error');
      const page = callbackPage('success', result.access_token);
      page.headers.set('Set-Cookie', 'oauth_state=; HttpOnly; Secure; SameSite=Lax; Path=/callback; Max-Age=0');
      return page;
    }
    return response('Not found', 404);
  },
};
