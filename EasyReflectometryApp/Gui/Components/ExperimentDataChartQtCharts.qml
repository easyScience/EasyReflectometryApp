import easyApp.Gui.Charts 1.0 as EaCharts

import Gui.Globals 1.0 as ExGlobals

EaCharts.BaseQtCharts {
    measuredData: ExGlobals.Constants.proxy.plotting1d.qtchartsMeasuredDataObj

    plotRanges: ExGlobals.Constants.proxy.plotting1d.experimentPlotRangesObj

    xAxisTitle: "q (Å-1)"
    yMainAxisTitle: "R(q)"
}
