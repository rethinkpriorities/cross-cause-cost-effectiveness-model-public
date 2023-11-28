// Takes an array of values and a binning function and converts them into an svg grid of colored rects.

const ONE_ONE = "#d53e4f";
const ONE_TWO = "pink";
const ONE_THREE = "purple";
const TWO_TWO = "gainsboro";
const TWO_THREE = "#add8e6";
const THREE_THREE = "#4577b2";

export const WaffleChart = ({
  bins,
  rows = 25,
  labels,
}: {
  // Bin function should reduce to reasonable number and provide pairs of categorizations.
  // The pairs of categorizations allow each square to represent two categories. (E.g. negative and zero)
  // Categorizations should be 0, 1, or 2.
  // E.g. each cageroziation whether the bin is negative (0), zero (1), or positive (2)
  /* binnedData: [0 | 1 | 2, 0 | 1 | 2][]; */
  bins: [number, number][];
  rows: number;
  labels: [string, string, string];
}) => {
  const numBins = bins.length;
  const cols = Math.floor(numBins / rows);
  const length = 3;
  const spacing = 9 / 8;
  return (
    <div className="mb-[2em] mt-[2em] flex justify-around">
      <div className="flex flex-col">
        <svg
          style={{ height: `${rows * 10}px`, width: `${cols * 10}px` }}
          viewBox={`0 0 ${cols * length * spacing} ${rows * length * spacing}`}
        >
          <g>
            {bins.map((bin, idx) => {
              const y = (idx % rows) * (length * spacing);
              const x = Math.floor(idx / rows) * (length * spacing);
              let color = "";
              if (bin[0] < 0 && bin[1] < 0) {
                color = ONE_ONE;
              } else if (bin[0] < 0 && bin[1] === 0) {
                color = ONE_TWO;
              } else if (bin[0] < 0 && bin[1] > 0) {
                color = ONE_THREE;
              } else if (bin[0] === 0 && bin[1] === 0) {
                color = TWO_TWO;
              } else if (bin[0] === 0 && bin[1] > 0) {
                color = TWO_THREE;
              } else {
                color = THREE_THREE;
              }
              return (
                <rect
                  key={`${x} ${y}`}
                  width={String(length)}
                  height={String(length)}
                  x={String(x)}
                  y={String(y)}
                  fill={color}
                />
              );
            })}
          </g>
        </svg>
        <div className="width-100 mt-1 text-center text-xs">
          <svg height="1em" width="1em" className="mr-1 align-middle">
            <rect
              height="10"
              stroke="darkred"
              strokeWidth="0.5"
              width="10"
              fill={ONE_ONE}
            />
          </svg>
          {labels[0]}
          <svg height="1em" width="1em" className="ml-5 mr-1 align-middle">
            <rect
              height="10"
              width="10"
              stroke="grey"
              strokeWidth="0.5"
              fill={TWO_TWO}
            />
          </svg>
          {labels[1]}
          <svg height="1em" width="1em" className="ml-5 mr-1 align-middle">
            <rect
              height="10"
              stroke="darkblue"
              strokeWidth="0.5"
              width="10"
              fill={THREE_THREE}
            />
          </svg>
          {labels[2]}
        </div>
      </div>
    </div>
  );
};
