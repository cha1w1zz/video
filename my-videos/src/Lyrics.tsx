import {
  AbsoluteFill,
  Composition,
  continueRender,
  delayRender,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const FPS = 30;
const fontFamily = "KanitLyric";

const waitForFont = delayRender("Loading lyric font");
Promise.all(
  [
    ["700", "Kanit-700-Latin.woff2"],
    ["800", "Kanit-800-Latin.woff2"],
  ].map(([weight, file]) =>
    new FontFace(fontFamily, `url(${staticFile(file)})`, { weight })
      .load()
      .then((f) => document.fonts.add(f)),
  ),
)
  .then(() => continueRender(waitForFont))
  .catch(() => continueRender(waitForFont));

type Line = { at: number; end: number; text: string; big?: boolean };

// Times in seconds of the output video.
const LINES: Line[] = [
  { at: 0.13, end: 3.7, text: "Take me down to the river" },
  { at: 3.9, end: 7.5, text: "Underneath the blood orange sun" },
  { at: 7.69, end: 11.3, text: "Say my name like a scripture" },
  { at: 11.47, end: 15.1, text: "Keep my heart beating like a drum" },
  { at: 15.25, end: 17.0, text: "LEGENDARY LOVERS", big: true },
  { at: 17.15, end: 18.9, text: "We could be legendary" },
  { at: 19.05, end: 22.6, text: "la-la-la-la-la" },
  { at: 22.8, end: 24.55, text: "LEGENDARY LOVERS", big: true },
  { at: 24.7, end: 26.45, text: "We should be legendary" },
  { at: 26.6, end: 30.0, text: "la-la-la-la-la" },
];

export const LyricsComposition = () => (
  <Composition
    id="Lyrics"
    component={Lyrics}
    durationInFrames={Math.round(30.5 * FPS)}
    fps={FPS}
    width={1920}
    height={1080}
  />
);

const Word: React.FC<{ word: string; startFrame: number; big?: boolean }> = ({
  word,
  startFrame,
  big,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({
    frame: frame - startFrame,
    fps,
    config: { damping: 11, stiffness: 220, mass: 0.6 },
  });
  const blur = interpolate(frame - startFrame, [0, 5], [12, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <span
      style={{
        display: "inline-block",
        margin: big ? "0 22px" : "0 12px",
        opacity: frame < startFrame ? 0 : 1,
        transform: `scale(${0.4 + pop * 0.6}) translateY(${(1 - pop) * 30}px)`,
        filter: `blur(${blur}px)`,
      }}
    >
      {word}
    </span>
  );
};

const LyricLine: React.FC<{ line: Line }> = ({ line }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  if (t < line.at || t > line.end) return null;

  const words = line.text.split(" ");
  const startF = Math.round(line.at * fps);
  const wordGap = line.big ? 4 : Math.max(3, Math.min(6, Math.floor(18 / words.length)));
  const fadeOut = interpolate(t, [line.end - 0.2, line.end], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const shake = line.big ? Math.sin(frame * 2.1) * 6 * Math.exp(-(t - line.at) * 3) : 0;

  return (
    <AbsoluteFill
      style={{
        justifyContent: line.big ? "center" : "flex-end",
        alignItems: "center",
        paddingBottom: line.big ? 0 : 150,
        opacity: fadeOut,
        transform: `translate(${shake}px, ${shake * 0.6}px)`,
      }}
    >
      <div
        style={{
          fontFamily,
          fontWeight: line.big ? 800 : 700,
          fontSize: line.big ? 170 : 78,
          letterSpacing: line.big ? 6 : 1,
          color: "#ffffff",
          textAlign: "center",
          maxWidth: 1700,
          textShadow: line.big
            ? "0 0 30px #ff4fd8, 0 0 70px #3ee7ff, 0 6px 0 rgba(0,0,0,0.5)"
            : "0 0 18px rgba(255,79,216,0.9), 0 0 40px rgba(62,231,255,0.7), 0 4px 0 rgba(0,0,0,0.6)",
        }}
      >
        {words.map((w, i) => (
          <Word key={i} word={w} startFrame={startF + i * wordGap} big={line.big} />
        ))}
      </div>
    </AbsoluteFill>
  );
};

export const Lyrics: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "transparent" }}>
    {LINES.map((l, i) => (
      <LyricLine key={i} line={l} />
    ))}
  </AbsoluteFill>
);
