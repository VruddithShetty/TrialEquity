import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Protected routes require an auth token
// Note: Auth token is stored in localStorage on client-side
// This middleware cannot access localStorage directly
// Instead, we let client-side route protection handle it via ClientLayout component
const PROTECTED_PREFIXES = [
  '/admin',
  '/upload',
  '/verifier',
  '/compare',
  '/ml-analysis',
  '/blockchain',
  '/regulator',
  '/files',
]

function isProtectedPath(pathname: string) {
  return PROTECTED_PREFIXES.some((p) => pathname.startsWith(p))
}

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl

  // Middleware cannot reliably check localStorage-based auth
  // Client-side components (ClientLayout, useEffect hooks) handle auth verification
  // This middleware only prevents navigation issues
  
  // Allow all routes through - client-side auth will handle redirects
  // This prevents middleware from blocking legitimate requests
  return NextResponse.next()
}

export const config = {
  matcher: [
    // Apply to all app routes except static assets and images
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
}
