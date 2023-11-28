import { useState } from "react";
import { CaptionTextContext } from "../../contexts/contexts";

export const Figure = ({
  children,
  name,
  caption,
}: {
  name: string;
  children: React.ReactNode;
  caption?: React.ReactNode;
}) => {
  const [moreCaptionText, setMoreCaptionText] = useState(<></>);

  const addToCaptionText = (value: React.ReactNode): undefined => {
    setMoreCaptionText(<>{value}</>);
  };
  return (
    <figure className="mb-10 mt-5">
      <CaptionTextContext.Provider value={addToCaptionText}>
        {children}
        <div className="mt-5">
          <figcaption className="block text-left text-sm">
            <strong>{name}.</strong> {caption}
            {moreCaptionText}
          </figcaption>
        </div>
      </CaptionTextContext.Provider>
    </figure>
  );
};
