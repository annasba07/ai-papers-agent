export default function TrendingWidgetSkeleton() {
  return (
    <div className="trending-skeleton">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="trending-skeleton__item">
          <div className="skeleton trending-skeleton__rank" />
          <div className="trending-skeleton__info">
            <div className="skeleton trending-skeleton__name" />
            <div className="skeleton trending-skeleton__count" />
          </div>
        </div>
      ))}
    </div>
  );
}
