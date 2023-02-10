#!/usr/bin/env python3
import cv2
import numpy as np
import argparse

def stitch(file1, file2, file_stitched, gray_scale = False):
    if gray_scale:
        img1 = cv2.imread(file1, cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imread(file2, cv2.IMREAD_GRAYSCALE)
    else:
        img1 = cv2.imread(file1)
        img2 = cv2.imread(file2)

    # Initiate SIFT detector
    sift = cv2.SIFT_create()

    # find the keypoints and descriptors
    kp1, descriptor1 = sift.detectAndCompute(img1, None)
    kp2, descriptor2 = sift.detectAndCompute(img2, None)
    kps1 = np.asarray([kp.pt for kp in kp1])
    kps2 = np.asarray([kp.pt for kp in kp2])

    # match
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(descriptor1,descriptor2, k=2)

    # store all the good matches
    good = []
    for m,n in matches:
        if m.distance < 0.7 * n.distance:
            good.append(m)

    if gray_scale:
        offset_y, offset_x= img1.shape
    else:
        offset_y, offset_x, _= img1.shape
    kps1_good = np.float32([kps1[m.queryIdx] + [offset_x, offset_y] for m in good])
    kps2_good = np.float32([kps2[m.trainIdx] for m in good])

    M, _ = cv2.findHomography(kps2_good, kps1_good, cv2.RANSAC, 5.0)

    dst_size = (int(img1.shape[1] * 4), int(img1.shape[0] * 4))
    # Perspective Transformation
    dst = cv2.warpPerspective(img2, M, dst_size)

    src = np.zeros_like(dst)
    src[offset_y:offset_y + img1.shape[0], offset_x:offset_x + img1.shape[1]] = img1


    np.putmask(dst, src, src)

    if gray_scale:
        y,x= dst.nonzero()
    else:
        y,x, _= dst.nonzero()
    minx = np.min(x)
    miny = np.min(y)
    maxx = np.max(x)
    maxy = np.max(y)
    dst = dst[miny:maxy, minx:maxx]

    cv2.imwrite(file_stitched, dst)


if '__main__' == __name__:
    # 解析命令
    parser = argparse.ArgumentParser(description='image stitching based on feature matching')
    parser.add_argument("file1", help = "first image")
    parser.add_argument("file2", help = "second image")
    parser.add_argument("file_merged",help = "output")
    parser.add_argument("-g","--gray_scale", action = "store_true", help = "if given, the output will be grayscale image")
    args = parser.parse_args()
    stitch(args.file1, args.file2,args.file_merged, args.gray_scale)