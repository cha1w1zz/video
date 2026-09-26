import "./index.css";
import { MyComposition } from "./Composition";
import { LyricsComposition } from "./Lyrics";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <MyComposition />
      <LyricsComposition />
    </>
  );
};
