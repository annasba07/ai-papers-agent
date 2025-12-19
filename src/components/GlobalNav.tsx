"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/explore", label: "Explore", icon: "compass" },
  { href: "/discovery", label: "Discovery", icon: "spark" },
  { href: "/generate", label: "Generate", icon: "code" },
];

const icons: Record<string, React.ReactNode> = {
  compass: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="10" />
      <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
    </svg>
  ),
  spark: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" />
    </svg>
  ),
  code: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="16 18 22 12 16 6" />
      <polyline points="8 6 2 12 8 18" />
    </svg>
  ),
};

export default function GlobalNav() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  // Redirect home to explore
  const isHome = pathname === "/";

  return (
    <header className="global-nav">
      <div className="global-nav__container">
        <Link href="/explore" className="global-nav__brand">
          <span className="global-nav__logo">
            {/* Compass Rose - Cartographic Atlas Icon */}
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              {/* Outer circle */}
              <circle cx="16" cy="16" r="14" stroke="currentColor" strokeWidth="1.5" fill="none"/>
              {/* Inner detail circle */}
              <circle cx="16" cy="16" r="10" stroke="currentColor" strokeWidth="0.75" fill="none" opacity="0.4"/>
              {/* North pointer (filled) */}
              <path d="M16 2L19 16L16 14L13 16L16 2Z" fill="currentColor"/>
              {/* South pointer (outline) */}
              <path d="M16 30L13 16L16 18L19 16L16 30Z" stroke="currentColor" strokeWidth="1" fill="none"/>
              {/* East pointer (outline) */}
              <path d="M30 16L16 13L18 16L16 19L30 16Z" stroke="currentColor" strokeWidth="1" fill="none"/>
              {/* West pointer (filled) */}
              <path d="M2 16L16 19L14 16L16 13L2 16Z" fill="currentColor"/>
              {/* Center dot */}
              <circle cx="16" cy="16" r="2" fill="currentColor"/>
            </svg>
          </span>
          <span className="global-nav__title">Paper Atlas</span>
        </Link>

        <button
          className="global-nav__toggle"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle navigation"
          aria-expanded={mobileOpen}
        >
          <span className={`global-nav__hamburger ${mobileOpen ? "global-nav__hamburger--open" : ""}`} />
        </button>

        <nav className={`global-nav__menu ${mobileOpen ? "global-nav__menu--open" : ""}`}>
          <ul className="global-nav__list">
            {navItems.map((item) => (
              <li key={item.href} className="global-nav__item">
                <Link
                  href={item.href}
                  className={`global-nav__link ${isActive(item.href) || (isHome && item.href === "/explore") ? "global-nav__link--active" : ""}`}
                  onClick={() => setMobileOpen(false)}
                >
                  <span className="global-nav__icon">{icons[item.icon]}</span>
                  <span className="global-nav__label">{item.label}</span>
                </Link>
              </li>
            ))}
          </ul>
        </nav>

      </div>
    </header>
  );
}
