import { CalculateMetadataFunction, Composition } from "remotion";
import {
  AbsoluteFill,
  Img,
  continueRender,
  delayRender,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const fontFamily = "NotoSansThaiLocal";

const waitForFont = delayRender("Loading Thai font");
const fontFace = new FontFace(
  fontFamily,
  `url(${staticFile("NotoSansThai.woff2")}) format("woff2")`,
);
fontFace
  .load()
  .then((loaded) => {
    document.fonts.add(loaded);
    continueRender(waitForFont);
  })
  .catch((err) => {
    console.error("Failed to load Thai font", err);
    continueRender(waitForFont);
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

export const MyComponent: React.FC<Props> = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const photoScale = spring({
    frame,
    fps,
    config: { damping: 200 },
    durationInFrames: 25,
  });
  const photoOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });

  const nameOpacity = interpolate(frame, [20, 38], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const nameY = interpolate(frame, [20, 38], [20, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const subOpacity = interpolate(frame, [45, 63], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const subY = interpolate(frame, [45, 63], [20, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const lineWidth = interpolate(frame, [70, 90], [0, 420], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(circle at 30% 30%, #14213d 0%, #060a14 65%)",
        fontFamily,
      }}
    >
      {/* Decorative grid dots, tech vibe */}
      <AbsoluteFill
        style={{
          backgroundImage:
            "radial-gradient(circle, rgba(0,229,255,0.15) 1px, transparent 1px)",
          backgroundSize: "42px 42px",
          opacity: 0.5,
        }}
      />

      <AbsoluteFill
        style={{
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "center",
          padding: "0 140px",
          gap: 100,
        }}
      >
        <div
          style={{
            width: 460,
            height: 460,
            borderRadius: "50%",
            padding: 8,
            background:
              "linear-gradient(135deg, #00e5ff 0%, #2563eb 50%, #7c3aed 100%)",
            opacity: photoOpacity,
            transform: `scale(${photoScale})`,
            boxShadow: "0 0 60px rgba(0, 229, 255, 0.35)",
          }}
        >
          <Img
            src={staticFile("toey.jpg")}
            style={{
              width: "100%",
              height: "100%",
              borderRadius: "50%",
              objectFit: "cover",
              display: "block",
            }}
          />
        </div>

        <div style={{ display: "flex", flexDirection: "column" }}>
          <div
            style={{
              opacity: nameOpacity,
              transform: `translateY(${nameY}px)`,
              color: "#ffffff",
              fontSize: 128,
              fontWeight: 700,
              letterSpacing: 2,
            }}
          >
            ตุ้ย
          </div>

          <div
            style={{
              opacity: subOpacity,
              transform: `translateY(${subY}px)`,
              color: "#5eead4",
              fontSize: 54,
              fontWeight: 500,
              marginTop: 20,
            }}
          >
            นักเรียนมัธยม สายวิทย์-คอมพิวเตอร์
          </div>

          <div
            style={{
              marginTop: 34,
              height: 6,
              width: lineWidth,
              borderRadius: 3,
              background:
                "linear-gradient(90deg, #00e5ff 0%, #7c3aed 100%)",
            }}
          />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
