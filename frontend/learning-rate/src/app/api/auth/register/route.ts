import { NextRequest } from "next/server";
import { NextResponse } from 'next/server';
import { RegistrationData } from "@/app/components/signup-signin/registration_form/form_registration";
import { createUser } from '@/data/auth-dto'

export async function POST(request: NextRequest) {
  const res: RegistrationData = await request.json()

  // push user to data base
  await createUser(res)

  // return success
  return NextResponse.json({ status: 200 });
}
  
