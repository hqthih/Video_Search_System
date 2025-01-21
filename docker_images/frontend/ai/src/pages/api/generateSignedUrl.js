import { Storage } from '@google-cloud/storage';
import { addMinutes } from 'date-fns';

const storage = new Storage();
const bucketName = 'video-search-keyframes-storage';

export default async function handler(req, res) {
  const { fileName } = req.query;
  const bucket = storage.bucket(bucketName);
  const file = bucket.file(fileName);

  const expires = addMinutes(new Date(), 60); // URL valid for 60 minutes
  const [url] = await file.getSignedUrl({
    version: 'v4',
    action: 'read',
    expires,
  });

  res.status(200).json({ url });
}