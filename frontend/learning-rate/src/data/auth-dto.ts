import client from "@/data/prisma";
import { RegistrationData } from "@/app/components/signup-signin/registration_form/form_registration";
import { compareHash } from "@/utils/password";
import { type User } from "next-auth";

export const createUser = async (data: RegistrationData) => {
    const { name, lastName, skillLevel, username, email, password } = data;

    return await client.$transaction(async (client) => {
        await client.user.create({
            data: {
                username: username,
                password: password,
                email: email,
                name: (name + " " + lastName),
            }
        });
        
        const uid = await client.user.findFirst({
            where: {
                email: email,
            },
            select: {
                id: true
            }
        });

        if(!uid) throw new Error("User ID not found, User Creation failed.")
            
        await client.userInfo.create({
            data: {
                userID: uid.id,
                skillLevelID: skillLevel,
                firstname: name,
                lastname: lastName,
            }
        });
    });
}


export const login = async (email: string, password: string) => {
    
        // get user password hash (or null if doesnt exist)
        const userRaw = await client.user.findUnique({
            where: {
              email: email
            },
            select: {
              id: true,
              email: true,
              password: true,
              username: true,
            }
          });
          
          if (!userRaw) {
            throw new Error("User not found.");
          }
          
          const userPasswordVerified = (await compareHash(userRaw.password, password)) ? userRaw : null;
  
          if (!userPasswordVerified) {
            throw new Error("Wrong Password.");
          }
  
          const user: User = {
            id: userPasswordVerified.id,
            email: userPasswordVerified.email,
          }

          return user;
}