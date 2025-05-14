import { NextRequest } from "next/server";
import { NextResponse } from 'next/server';

const rateLimitMap = new Map<string, { count: number, lastReset: number }>();

export default async function rateLimitMiddleware(req: NextRequest): Promise<NextResponse | null> {
        const forwardedFor = req.headers.get("x-forwarded-for");
        const ip = forwardedFor ? forwardedFor.split(",")[0].trim() : req.ip;

        const limit = 100; // Limiting requests to 100 per minute per IP
        const windowMs = 60 * 1000; // 1 minute

        if (!ip) {
            return new NextResponse("Unable to determine IP address", { status: 400 });
        }
        
        if (!rateLimitMap.has(ip)) {
            rateLimitMap.set(ip, {
                count: 0,
                lastReset: Date.now(),
            });
        }
        
        const ipData = rateLimitMap.get(ip);

        if (!ipData) {
            return new NextResponse("Error retrieving rate limit data", { status: 500 });
        }
        
        if (Date.now() - ipData.lastReset > windowMs) {
            ipData.count = 0;
            ipData.lastReset = Date.now();
        }
        
        if (ipData.count >= limit) {
            return new NextResponse("Too Many Requests", { status: 429 });
        }
        
        ipData.count += 1;
        
        return null
}