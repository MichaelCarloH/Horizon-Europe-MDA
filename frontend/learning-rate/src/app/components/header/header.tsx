import React from "react";
import Image from "next/image";
import Link from "next/link";
import UserHeader from "@/app/components/header/user_header";

const Header = async () => {
  return (
    <header className="text-white body-font bg-sky-700" data-testid="header">
      <div className="container mx-auto flex flex-wrap p-5 flex-col md:flex-row items-center">
        <a
          href="#"
          className="flex title-font font-medium items-center md:justify-start justify-center text-gray-900"
          data-testid="logo-link"
        >
          <Image
            src={"/websitelogo.png"}
            alt="Logo"
            width={40}
            height={40}
            className="bg-blue-950 rounded-full"
            data-testid="logo-image"
          />
          <span className="ml-3 text-xl text-white" data-testid="company-name">
            Learning Rate
          </span>
        </a>
        <nav
          className="md:mr-auto md:ml-4 md:py-1 md:pl-4 md:border-l md:border-gray-400 flex flex-wrap items-center text-base justify-center"
          data-testid="nav"
        >
          <Link className="mr-5 hover:text-gray-900" href="/" data-testid="nav-home">
            Home
          </Link>
          <Link className="mr-5 hover:text-gray-900" href="/lessons" data-testid="nav-lessons">
            Lessons
          </Link>
          <a className="mr-5 hover:text-gray-900" href="/playground" data-testid="nav-playground">
            Playground
          </a>
          <Link className="mr-5 hover:text-gray-900" href="/about" data-testid="nav-about">
            About Us
          </Link>
        </nav>
        <UserHeader />
      </div>
    </header>
  );
};

export default Header;
