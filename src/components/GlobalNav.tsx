"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/", label: "Home", icon: "home" },
  { href: "/discovery", label: "Discovery", icon: "radar", isNew: true },
  { href: "/trends", label: "Trends", icon: "trending" },
  { href: "/atlas-explore", label: "Atlas", icon: "explore" },
  { href: "/generate", label: "Code Gen", icon: "code" },
];

const icons: Record<string, React.ReactNode> = {
  home: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
      <polyline points="9 22 9 12 15 12 15 22" />
    </svg>
  ),
  radar: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="10" />
      <circle cx="12" cy="12" r="6" />
      <circle cx="12" cy="12" r="2" />
      <path d="M12 2v4M12 18v4M2 12h4M18 12h4" />
    </svg>
  ),
  trending: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
      <polyline points="17 6 23 6 23 12" />
    </svg>
  ),
  explore: (
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

  return (
    <header className="global-nav">
      <div className="global-nav__container">
        <Link href="/" className="global-nav__brand">
          <span className="global-nav__logo">
            <svg width="28" height="28" viewBox="0 0 32 32" fill="none">
              <circle cx="16" cy="16" r="14" stroke="currentColor" strokeWidth="2" />
              <circle cx="16" cy="16" r="6" fill="currentColor" />
              <path d="M16 2v6M16 24v6M2 16h6M24 16h6" stroke="currentColor" strokeWidth="2" />
            </svg>
          </span>
          <span className="global-nav__title">AI Paper Atlas</span>
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
                  className={`global-nav__link ${isActive(item.href) ? "global-nav__link--active" : ""}`}
                  onClick={() => setMobileOpen(false)}
                >
                  <span className="global-nav__icon">{icons[item.icon]}</span>
                  <span className="global-nav__label">{item.label}</span>
                  {item.isNew && <span className="global-nav__badge">New</span>}
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
