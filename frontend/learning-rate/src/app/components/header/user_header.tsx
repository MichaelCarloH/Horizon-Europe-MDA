import React from "react";
import RegisterButton from "./register_button";
import LoginButton from "./login_button";
import { auth } from "@/auth";
import UserInfo from "./user_info";
import SignOutButton from "./signout_button";



const UserHeader = async () => {
    const session = await auth();

    const levelsJSON = await fetch(`${process.env.URL}/api/webinfo/skills`, { next: { revalidate: 1 * 60 * 60 } });
    const levels: {
        skillLevelID: number;
        skillname: string;
    }[] = await levelsJSON.json();
    
    return (
        <div>
            {
            (!session || !session.user) ?
                (<div className="flex flex-row justify-center items-center">
                    <RegisterButton levels={levels}/>
                    <LoginButton/>
                </div>)
            :
                (<div className="flex flex-col items-end">
                    <UserInfo/>
                    <SignOutButton/>
                </div>)
            }
        </div>
    );

    
}

export default UserHeader;