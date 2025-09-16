import React from "react";

type Variant = "light" | "dark"; // background intent
type Lockup = "wordmark" | "horizontal" | "vertical" | "mark";

export interface LogoProps {
  variant?: Variant;   // 'light' for dark BG, 'dark' for light BG
  lockup?: Lockup;     // wordmark/horizontal/vertical/mark
  height?: number;     // px
  className?: string;
}

const assets = {
  wordmark: {
    light: "/assets/CI_wordmark_terminal_light.svg",
    dark: "/assets/CI_wordmark_terminal_dark.svg"
  },
  horizontal: {
    light: "/assets/CI_lockup_horizontal.svg",
    dark: "/assets/CI_lockup_horizontal.svg"
  },
  vertical: {
    light: "/assets/CI_lockup_vertical.svg",
    dark: "/assets/CI_lockup_vertical.svg"
  },
  mark: {
    light: "/assets/CI_mark_boom.svg",
    dark: "/assets/CI_mark_boom.svg"
  }
};

export default function Logo({ variant = "dark", lockup = "wordmark", height = 40, className = "" }: LogoProps){
  const src = (assets as any)[lockup][variant];
  return <img src={src} height={height} style={{height}} className={className} alt="Crane Intelligence" />;
}
