export default function PaperCardSkeleton() {
  return (
    <div className="paper-card-skeleton">
      <div className="paper-card-skeleton__badges">
        <div className="skeleton paper-card-skeleton__badge" />
        <div className="skeleton paper-card-skeleton__badge" />
      </div>
      <div className="skeleton paper-card-skeleton__title" />
      <div className="skeleton paper-card-skeleton__authors" />
      <div className="skeleton paper-card-skeleton__abstract" />
      <div className="paper-card-skeleton__meta">
        <div className="skeleton paper-card-skeleton__meta-item" />
        <div className="skeleton paper-card-skeleton__meta-item" />
        <div className="skeleton paper-card-skeleton__meta-item" />
      </div>
    </div>
  );
}
