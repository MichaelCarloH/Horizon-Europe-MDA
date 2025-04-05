"use server"

import { signIn, providerMap } from "@/auth";

export const loginAction = async (formData: FormData) => {
    await signIn(providerMap.findLast(() => true)?.id, formData);
}
