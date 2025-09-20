import React, { useState } from "react";

const Image = ({ imgSrc, className }) => {
  const publicPath = process.env.PUBLIC_URL || "";
  const [imageError, setImageError] = useState(false);

  const isExternalLink = imgSrc && imgSrc.startsWith("http");

  const resolvedSrc = imageError
    ? `${publicPath}/default-image.png`
    : isExternalLink
    ? imgSrc
    : `${publicPath}/${imgSrc}.png`;

  return (
    <img
      className={className}
      src={resolvedSrc}
      alt="Imagem do Produto"
      onError={() => setImageError(true)} 
    />
  );
};

export default Image;
