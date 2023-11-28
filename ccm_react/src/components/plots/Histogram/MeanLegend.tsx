export const MeanLegend = () => {
  return (
    <>
      <div className="mr-[1em] mt-[.3em] w-100 flex flex-row md:w-auto">
        <span
          className="mr-1 text-xs"
          style={{
            fontFamily: "var(--default-font-family)",
          }}
        >
          Median
        </span>{" "}
        <svg className="h-[.8rem] w-[2em] fill-slate-700 stroke-slate-700 dark:fill-slate-200 dark:stroke-slate-200">
          <line
            x1="0"
            x2="100"
            y1="10"
            y2="10"
            strokeWidth="2.5"
            strokeDasharray="5,5"
          ></line>
        </svg>
        <span
          className="ml-5 mr-1 text-xs"
          style={{
            fontFamily: "var(--default-font-family)",
          }}
        >
          Mean
        </span>{" "}
        <svg className="h-[.8rem] w-[2em] fill-slate-700 stroke-slate-700 dark:fill-slate-200 dark:stroke-slate-200">
          <line x1="0" x2="100" y1="10" y2="10" strokeWidth="2.5"></line>
        </svg>
      </div>
    </>
  );
};
