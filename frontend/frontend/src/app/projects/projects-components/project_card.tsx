'use client'

import React from "react"
import Image from "next/image";
import Link from "next/link";

function ProjectCard(props: { title: string; tag: string; text: string; imgLink: string; isLocked: number; lessonLink: string }) {
    return (
        <div className="flex flex-col justify-between m-4 w-1/4 h-auto border-2 border-gray-200 border-opacity-60 rounded-lg relative">
            {props.isLocked === 1 && <div className="absolute top-0 left-0 w-full h-full bg-black/40 z-40"></div>}
            <Image
                className="self-center"
                width={450}
                height={293}
                src={props.imgLink}
                alt="blog"
            />
            <div className="p-6 text-wrap">
                <h2 className="tracking-widest text-xs title-font font-medium text-gray-400 mb-1">{props.title}</h2>
                <h1 className="title-font text-lg font-medium text-gray-900 mb-3">{props.tag}</h1>
                <p className="leading-relaxed mb-3">{props.text}</p>
            </div>
            <div className="p-6">
                <div className="flex justify-center items-center flex-wrap">
                    <button className={"flex text-center justify-center items-center text-black text-xl bg-sky-700 border-0 py-2 px-6 focus:outline-none rounded-lg shadow-xl w-full" + (props.isLocked ? " pointer-events-none" : "")}>
                        <Link href={"." + props.lessonLink}>Start</Link>
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ProjectCard; 