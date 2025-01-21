import { useEffect, useState } from 'react';

function ImageComponent({ fileName }) {
  const [imageUrl, setImageUrl] = useState('');

  useEffect(() => {
    async function fetchImageUrl() {
      const res = await fetch(`/api/generateSignedUrl?fileName=${fileName}`);
      const data = await res.json();
      setImageUrl(data.url);
    }

    fetchImageUrl();
  }, [fileName]);

  return <img src={imageUrl} alt="KeyFrame" />;
}

export default ImageComponent;