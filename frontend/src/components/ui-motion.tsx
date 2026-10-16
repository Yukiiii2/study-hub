"use client";

import { useEffect, useRef, type RefObject } from "react";

function timing(element: Element, token: "--duration-fast" | "--duration-normal") {
  const style = window.getComputedStyle(element);
  // CSS optimizers may normalize 160ms to .16s; WAAPI always expects milliseconds.
  const raw = style.getPropertyValue(token).trim(), parsed = Number.parseFloat(raw);
  const duration = Number.isFinite(parsed) && parsed >= 0 ? parsed * (raw.endsWith("ms") ? 1 : raw.endsWith("s") ? 1000 : 1) : token === "--duration-fast" ? 160 : 200;
  return { duration, easing: style.getPropertyValue("--ease-out").trim() || "ease-out" };
}

/** Animate existing page content, never key/remount it or move the persistent shell. */
export function usePageMotion(content: RefObject<HTMLElement | null>, pathname: string) {
  useEffect(() => {
    const targets = Array.from(content.current?.children ?? []).filter(target => typeof target.animate === "function" && !["DIALOG", "SCRIPT", "STYLE"].includes(target.tagName));
    if (!targets.length) return;
    const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (preference.matches) return;
    const animations = targets.map(target => target.animate([{ opacity: 0, transform: "translateY(4px)" }, { opacity: 1, transform: "none" }], timing(target, "--duration-normal")));
    const cancel = () => animations.forEach(animation => animation.cancel());
    preference.addEventListener("change", cancel);
    return () => { preference.removeEventListener("change", cancel); cancel(); };
  }, [content, pathname]);
}

/** Manual dismissal only. Successful saves keep their existing immediate close path. */
export function useDialogDismiss(dialog: RefObject<HTMLDialogElement | null>, dismiss: () => void) {
  const animation = useRef<Animation | null>(null);
  useEffect(() => () => animation.current?.cancel(), []);
  return () => {
    if (animation.current) return;
    const element = dialog.current;
    if (!element || typeof element.animate !== "function" || window.matchMedia("(prefers-reduced-motion: reduce)").matches) { element?.close(); dismiss(); return; }
    const mobile = window.matchMedia("(max-width: 600px)").matches;
    const tablet = window.matchMedia("(max-width: 959px)").matches;
    element.dataset.motionClosing = "true";
    const exit = element.animate([{ opacity: 1, transform: "none" }, { opacity: 0, transform: mobile ? "translateY(8px)" : tablet ? "translateX(6px)" : "scale(.98)" }], timing(element, "--duration-fast"));
    animation.current = exit;
    const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
    let finished = false;
    const finish = () => { if (finished) return; finished = true; preference.removeEventListener("change", finish); element.close(); dismiss(); };
    exit.onfinish = finish;
    exit.oncancel = () => { preference.removeEventListener("change", finish); animation.current = null; delete element.dataset.motionClosing; };
    preference.addEventListener("change", finish, { once: true });
  };
}
