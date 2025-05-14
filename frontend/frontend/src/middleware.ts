import csrfProtect from "@/middleware/csrf";
import rateLimit from "@/middleware/rate-limit";
import { CsrfError } from "@edge-csrf/nextjs";
import { NextRequest, NextResponse } from "next/server";

export const middleware = async (request: NextRequest) => {
    const response = NextResponse.next();

    if (request.nextUrl.pathname.startsWith('/api/auth/signout')) {
      return NextResponse.next()
    }

    if(!request.headers.has('Next-Action')) {
      try {
        await csrfProtect(request, response);
      } catch (err) {
        if (err instanceof CsrfError) return new NextResponse('Invalid csrf token.', { status: 403 });
        throw err;
      }
    }

    const rateLimitResponse = await rateLimit(request);
    if (rateLimitResponse) {
      return rateLimitResponse;
    }
    
    return response;
  };


