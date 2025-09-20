import React from "react";
import { AiOutlineCopyright } from "react-icons/ai";

const FooterBottom = () => {
  return (
    <footer className="w-full bg-[#F5F5F3]">
      <div className="max-w-container mx-auto border-t-[1px] pt-4 pb-4">
        <p className="text-titleFont font-normal text-center flex md:items-center justify-center text-lightText duration-200 text-sm">
          <span className="text-md mr-[1px] mt-[2px] md:mt-0 text-center hidden md:inline-flex">
            <AiOutlineCopyright />
          </span>
          Copyright 2024 | Voltix | All Rights Reserved
        </p>
      </div>
    </footer>
  );
};

export default FooterBottom;