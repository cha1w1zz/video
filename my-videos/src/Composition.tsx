import { CalculateMetadataFunction, Composition } from "remotion";
import {
  AbsoluteFill,
  Img,
  continueRender,
  delayRender,
  interpolate,
  random,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const fontFamily = "KanitLocal";

const waitForFonts = delayRender("Loading Kanit font");
Promise.all(
  [
    ["400", "Kanit-Regular-Thai.woff2"],
    ["700", "Kanit-Bold-Thai.woff2"],
    ["800", "Kanit-ExtraBold-Thai.woff2"],
  ].map(([weight, file]) => {
    const face = new FontFace(fontFamily, `url(${staticFile(file)})`, {
      weight,
    });
    return face.load().then((loaded) => document.fonts.add(loaded));
  }),
)
  .then(() => continueRender(waitForFonts))
  .catch((err) => {
    console.error("Failed to load Kanit font", err);
    continueRender(waitForFonts);
  });

type Props = {};

const calculateMetadata: CalculateMetadataFunction<Props> = () => {
  return {};
};

const FPS = 30;
const DURATION_IN_SECONDS = 5;

export const MyComposition = () => {
  return (
    <Composition
      id="TechIntro"
      component={MyComponent}
      durationInFrames={DURATION_IN_SECONDS * FPS}
      fps={FPS}
      width={1920}
      height={1080}
      calculateMetadata={calculateMetadata}
    />
  );
};

const Blob: React.FC<{
  seed: string;
  size: number;
  color: string;
  top: string;
  left: string;
}> = ({ seed, size, color, top, left }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const floatY = Math.sin(frame / fps + random(seed) * 10) * 24;
  const floatX = Math.cos(frame / fps + random(seed + "x") * 10) * 18;
  const appear = spring({ frame, fps, config: { damping: 200 } });

  return (
    <div
      style={{
        position: "absolute",
        top,
        left,
        width: size,
        height: size,
        borderRadius: "50%",
        background: color,
        filter: "blur(2px)",
        opacity: 0.85 * appear,
        transform: `translate(${floatX}px, ${floatY}px) scale(${appear})`,
      }}
    />
  );
};

export const MyComponent: React.FC<Props> = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const bgHueShift = interpolate(frame, [0, 150], [0, 40]);

  const photoBounce = spring({
    frame,
    fps,
    config: { damping: 10, stiffness: 120, mass: 0.9 },
    durationInFrames: 30,
  });
  const photoRotate = interpolate(photoBounce, [0, 1], [-14, -6]);
  const photoOpacity = interpolate(frame, [0, 10], [0, 1], {
    extrapolateRight: "clamp",
  });

  const nameBounce = spring({
    frame: frame - 16,
    fps,
    config: { damping: 9, stiffness: 140, mass: 0.8 },
    durationInFrames: 28,
  });
  const nameOpacity = interpolate(frame, [16, 26], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const subOpacity = interpolate(frame, [40, 55], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const subY = interpolate(frame, [40, 55], [30, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: (t) => 1 - Math.pow(1 - t, 3),
  });

  const badgeScale = spring({
    frame: frame - 65,
    fps,
    config: { damping: 8, stiffness: 160, mass: 0.7 },
    durationInFrames: 25,
  });
  const badgeOpacity = interpolate(frame, [65, 78], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const sparkleOpacity = interpolate(frame, [85, 100, 140, 150], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(135deg, hsl(${300 + bgHueShift}, 85%, 62%) 0%, hsl(${255 + bgHueShift}, 90%, 58%) 45%, hsl(${200 + bgHueShift}, 95%, 55%) 100%)`,
        fontFamily,
        overflow: "hidden",
      }}
    >
      <Blob seed="a" size={340} color="#ffe66d" top="-60px" left="70%" />
      <Blob seed="b" size={220} color="#ff6bcb" top="70%" left="5%" />
      <Blob seed="c" size={160} color="#5ef2ff" top="10%" left="8%" />
      <Blob seed="d" size={120} color="#a78bfa" top="78%" left="82%" />

      <AbsoluteFill
        style={{
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "center",
          padding: "0 120px",
          gap: 90,
        }}
      >
        <div
          style={{
            width: 480,
            height: 480,
            borderRadius: 40,
            padding: 14,
            background: "#ffffff",
            position: "relative",
            opacity: photoOpacity,
            transform: `rotate(${photoRotate}deg) scale(${photoBounce})`,
            boxShadow: "0 30px 60px rgba(0,0,0,0.35)",
          }}
        >
          <Img
            src={staticFile("toey.jpg")}
            style={{
              width: "100%",
              height: "100%",
              borderRadius: 28,
              objectFit: "cover",
              display: "block",
            }}
          />
          <div
            style={{
              position: "absolute",
              bottom: -22,
              right: -22,
              background: "#0f172a",
              color: "#ffe66d",
              fontWeight: 800,
              fontSize: 30,
              padding: "10px 22px",
              borderRadius: 999,
              transform: `scale(${badgeScale}) rotate(-6deg)`,
              opacity: badgeOpacity,
              boxShadow: "0 10px 24px rgba(0,0,0,0.3)",
              whiteSpace: "nowrap",
            }}
          >
            ✦ SCI-COM ✦
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column" }}>
          <div
            style={{
              opacity: nameOpacity,
              transform: `scale(${0.7 + nameBounce * 0.3}) rotate(${(1 - nameBounce) * -4}deg)`,
              transformOrigin: "left center",
              color: "#ffffff",
              fontSize: 156,
              fontWeight: 800,
              letterSpacing: 1,
              textShadow: "0 8px 0 rgba(15,23,42,0.35)",
            }}
          >
            ตุ้ย
          </div>

          <div
            style={{
              opacity: subOpacity,
              transform: `translateY(${subY}px)`,
              display: "inline-flex",
              marginTop: 8,
            }}
          >
            <div
              style={{
                color: "#0f172a",
                background: "#ffe66d",
                fontSize: 48,
                fontWeight: 700,
                padding: "10px 28px",
                borderRadius: 999,
                boxShadow: "0 8px 0 rgba(15,23,42,0.25)",
              }}
            >
              นักเรียนสายวิทย์-คอมพิวเตอร์ 💻
            </div>
          </div>

          <div
            style={{
              marginTop: 30,
              color: "#ffffff",
              fontSize: 34,
              fontWeight: 400,
              opacity: sparkleOpacity,
            }}
          >
            ⚡ พร้อมลุยทุกความท้าทายสายเทค ⚡
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
