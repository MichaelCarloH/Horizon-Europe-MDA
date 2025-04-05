import React from "react";
import { auth } from "@/auth";
import { getCurrentUserInfo } from "@/data/user-dto";


const UserInfo = async () => {
    const session = await auth();
    const uinfo = await getCurrentUserInfo(session);

    return (
        <div className="flex flex-col justify-end items-end bg-blue-950 p-2 px-10 rounded-2xl shadow-xl">
            <h1 className="text-3xl pb-0.5"> { uinfo?.username }  </h1>
            <p className="text-base"> { uinfo?.firstname + " " + uinfo?.lastname }  </p>

        </div>
    )
}

export default UserInfo;