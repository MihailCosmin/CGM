﻿using System.Collections.Generic;
using System.Linq;
using codessentials.CGM.Commands;

namespace codessentials.CGM.Classes
{
    /// <summary>
    /// Engine to recognize geograpical objects
    /// </summary>
    public class GeometryRecognitionEngine
    {
        /// <summary>
        /// Gets all rectangles of the given file.
        /// </summary>
        /// <param name="file">The file.</param>
        /// <returns></returns>
        public static List<CgmRectangle> GetRectangles(CgmFile file)
        {
            var result = new List<CgmRectangle>();

            // sort all polylines by their points
            var polylines = file.Commands.Where(c => c.ElementClass == ClassCode.GraphicalPrimitiveElements && (c.ElementId == 1)).Cast<Polyline>().ToList(); //Polyline

            // now we have a list with such items
            // LINE(125.2167, 136.3638) (125.2167, 145.3638);
            // LINE(125.2167, 136.3638) (150.8740, 136.3638);
            // LINE(150.8741, 145.3638) (125.2167, 145.3638);
            // LINE(150.8740, 136.3638) (150.8740, 145.3638);
            //
            // this example (5 simple lines) above describes a rectangle

            // internaly we see all points in a sorted way like that
            // (81.3296,95.3243)
            // (81.3296,105.3844)
            // (81.3296,105.3844)
            // (101.4332,95.3243)
            // (101.4332,105.3844)
            //
            // this example (5 points) above describes a rectangle (third line can be ommited)

            var simpleLines = polylines.Where(l => l.IsSimpleLine);
            var rectangleCanditates = polylines.Where(l => l.Points.Length == 5);

            result.AddRange(FindRectangleInSimpleLines(simpleLines));
            result.AddRange(FindRectangleInPolygons(rectangleCanditates));


            return result;
        }

        private static IEnumerable<CgmRectangle> FindRectangleInPolygons(IEnumerable<Polyline> rectangleCanditates)
        {
            var result = new List<CgmRectangle>();
            foreach (var line in rectangleCanditates)
            {
                var rectangle = GetRectangle(line);

                if (!rectangle.IsEmpty)
                    result.Add(rectangle);
            }

            return result;
        }

        private static IEnumerable<CgmRectangle> FindRectangleInSimpleLines(IEnumerable<Polyline> simpleLines)
        {
            // get all horizontal lines
            var horizontalLines = simpleLines.Where(l => IsHorizontalLine(l.Points[0], l.Points[1])).Select(l => new CgmLine(l.Points[0], l.Points[1]));
            var verticalLines = simpleLines.Where(l => IsVerticalLine(l.Points[0], l.Points[1])).Select(l => new CgmLine(l.Points[0], l.Points[1]));
            var rects = new List<RectanglePoints>();

            // loop through horizontal lines and find the two parelles each
            foreach (var horzLine in horizontalLines)
            {
                var others = horizontalLines.Where(l => CgmPoint.IsSame(l.A.X, horzLine.A.X) && l.A.Y > horzLine.A.Y);

                if (others.Any())
                {
                    var nearest = others.OrderBy(l => l.A.Y).Last();
                    rects.Add(new RectanglePoints(horzLine, nearest));
                }
            }

            // loop the vertical lines and find the ones linking to the horizontal ones
            foreach (var verticalLine in verticalLines)
            {
                var l = rects.FirstOrDefault(h => h.IsUpperLeft(verticalLine.A));

                if (l != null && l.IsLowerLeft(verticalLine.B))
                {
                    l.SetLowerLeft(verticalLine.B);
                    continue;
                }

                l = rects.FirstOrDefault(h => h.IsUpperRight(verticalLine.A));

                if (l != null && l.IsLowerRight(verticalLine.B))
                {
                    l.SetLowerRight(verticalLine.B);
                }
            }

            return rects.Where(r => r.IsValid).Select(r => r.ToRectangle());
        }

        private static bool IsHorizontalLine(CgmPoint a, CgmPoint b)
        {
            return CgmPoint.IsSame(a.Y, b.Y) && !CgmPoint.IsSame(a.X, b.X);
        }

        private static bool IsVerticalLine(CgmPoint a, CgmPoint b)
        {
            return CgmPoint.IsSame(a.X, b.X) && !CgmPoint.IsSame(a.Y, b.Y);
        }


        public static CgmRectangle GetRectangle(Polyline polyline)
        {
            if (IsRectangle(polyline))
            {
                var points = polyline.Points;

                // rectangle is descriped counter clock-wise starting right
                if (CgmPoint.IsSame(points[0].Y, points[1].Y) && CgmPoint.IsSame(points[1].X, points[2].X) && CgmPoint.IsSame(points[2].Y, points[3].Y))
                {
                    if (points[1].Y < points[2].Y)
                        return CgmRectangle.FromPoints(points[1], points[0], points[2], points[3]);
                    else if (points[0].X < points[1].X) // starting left
                        return CgmRectangle.FromPoints(points[3], points[2], points[0], points[1]);
                    else
                        return CgmRectangle.FromPoints(points[2], points[3], points[1], points[0]);
                }

                // rectangle is described clock wise 
                if (CgmPoint.IsSame(points[0].X, points[1].X) && CgmPoint.IsSame(points[1].Y, points[2].Y) && CgmPoint.IsSame(points[2].X, points[3].X))
                {
                    return CgmRectangle.FromPoints(points[4], points[0], points[3], points[1]);
                }
            }

            return CgmRectangle.Empty;
        }

        private static bool IsRectangle(Polyline polyline)
        {
            if (polyline.Points.Length == 5)
            {

                // internaly we see all points in a sorted way like that
                // (81.3296,95.3243)
                // (81.3296,105.3844)
                // (81.3296,105.3844)
                // (101.4332,95.3243)
                // (101.4332,105.3844)
                //
                // this example (5 points) above describes a rectangle (third line can be ommited)

                // last should close the path
                return (polyline.Points[0].Equals(polyline.Points[4]));
            }

            return false;
        }

        /// <summary>
        /// Determines whether point A is near point b
        /// </summary>
        /// <param name="pointA">The start point.</param>
        /// <param name="pointWithinRange">The point with have to be within the range of the start point.</param>
        /// <param name="rangeDistance">The range distance.</param>
        public static bool IsNearBy(CgmPoint pointA, CgmPoint pointWithinRange, float rangeDistance)
        {
            var rect = new CgmRectangle((float)pointA.X - rangeDistance, (float)pointA.Y - rangeDistance, rangeDistance * 2, rangeDistance * 2);

            return rect.Contains(pointWithinRange);
        }

        private class RectanglePoints
        {
            CgmLine _topLine;
            CgmLine _bottomLine;
            CgmPoint _leftLowerCorner;
            CgmPoint _rightLowerCorner;

            public bool IsValid
            {
                get { return _leftLowerCorner != null && _rightLowerCorner != null && GetIsValid(_topLine.A, _topLine.B, _leftLowerCorner, _rightLowerCorner); }
            }

            public RectanglePoints(CgmLine topLine, CgmLine bottomLine)
            {
                _topLine = topLine;
                _bottomLine = bottomLine;
            }

            public bool IsUpperLeft(CgmPoint p)
            {
                return _topLine.A.CompareTo(p) == 0;
            }

            public bool IsLowerLeft(CgmPoint p)
            {
                return _bottomLine.A.CompareTo(p) == 0;
            }

            public bool IsUpperRight(CgmPoint p)
            {
                return _topLine.B.CompareTo(p) == 0;
            }

            public bool IsLowerRight(CgmPoint p)
            {
                return _bottomLine.B.CompareTo(p) == 0;
            }

            public void SetLowerLeft(CgmPoint p)
            {
                _leftLowerCorner = p;
            }

            public void SetLowerRight(CgmPoint p)
            {
                _rightLowerCorner = p;
            }

            private static bool GetIsValid(CgmPoint leftUpperCorner, CgmPoint rightUpperCorner, CgmPoint leftLowerCorner, CgmPoint rightLowerCorner)
            {
                if (leftUpperCorner.Y != rightUpperCorner.Y)
                    return false;

                if (leftLowerCorner.Y != rightLowerCorner.Y)
                    return false;

                if (leftUpperCorner.X != leftLowerCorner.X)
                    return false;

                if (rightUpperCorner.X != rightLowerCorner.X)
                    return false;

                return true;
            }

            public CgmRectangle ToRectangle()
            {
                return CgmRectangle.FromPoints(_topLine.A, _topLine.B, _leftLowerCorner, _rightLowerCorner);
            }
        }
    }
}
