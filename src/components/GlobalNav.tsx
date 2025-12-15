"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/explore", label: "Explore", icon: "compass" },
  { href: "/generate", label: "Generate", icon: "code" },
];

const icons: Record<string, React.ReactNode> = {
  compass: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="10" />
      <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
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

        <div className="global-nav__actions">
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="global-nav__action"
            title="View on GitHub"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
            </svg>
          </a>
        </div>
      </div>
    </header>
  );
}
