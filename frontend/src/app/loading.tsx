import {
  barStyles,
  captionStyles,
  containerStyles,
  logoStyles,
  trackStyles,
} from "./loading.styles";

export default function Loading() {
  return (
    <div className={containerStyles}>
      <div className={logoStyles}>App</div>
      <div className={trackStyles}>
        <div className={barStyles} />
      </div>
      <div className={captionStyles}>Synchronizing Neural Link...</div>
    </div>
  );
}
