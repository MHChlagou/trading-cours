import React from 'react';

/** Figure avec légende : image (src) ou SVG inline (children). */
export default function Figure({caption, alt, src, children}) {
  return (
    <figure className="tm-figure">
      {src ? <img src={src} alt={alt || caption || ''} /> : children}
      {caption && <figcaption>{caption}</figcaption>}
    </figure>
  );
}
