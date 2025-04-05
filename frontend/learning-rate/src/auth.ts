import NextAuth, { type DefaultSession } from "next-auth";
import Credentials from "next-auth/providers/credentials";
import { login } from "./data/auth-dto";
import type { Provider } from "next-auth/providers"

const SESSION_MAX_AGE = 1* 60 * 60 // 1 hour

declare module "next-auth" {
  interface User {
    id?: string,
    email?: string | null,
  }

  interface Session {
    user: User & DefaultSession["user"]
  } 
}

const providers: Provider[] = [
  Credentials({ // credentials cannot support adapters

    credentials: {
      email: {label: "Email", type: "email"},
      password: {label: "Password", type: "password"},
    },
    
    authorize: async (credentials) => {
      const email: string = typeof credentials.email == 'string' ? credentials.email : '';
      const password: string = typeof credentials.password == 'string' ? credentials.password : '';
      
      const user = await login(email, password);

      return user;
    },
  }),
];

export const providerMap = providers.map((provider) => {
  if (typeof provider === "function") {
    const providerData = provider()
    return { id: providerData.id, name: providerData.name }
  } else {
    return { id: provider.id, name: provider.name }
  }
});

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: providers,

  session: {
    strategy: "jwt",
    maxAge: SESSION_MAX_AGE,
  },

  pages: {
    signIn: "/login",
  },
  
  callbacks:{

    async jwt ({ token, user }) {
      if (user?.id) token._id = user.id;
      return token;
    },

    async session ({ session, token, user }) {
        // user id is stored in ._id when using credentials provider
        if (token?._id) session.user.id = token._id as string;
    
        return session
    },
  },
})