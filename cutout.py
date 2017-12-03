import sys
import time
from PIL import Image
from random import randint

img_row = 0
img_col = 0
time_start = 0
parent = []

def valid(a, b):
	global img_row
	global img_col
	return a < img_row and a >= 0 and b < img_col and b >= 0

def jarak(a,b):
	c = 0
	for i in range(3):
			c += (a[i] - b[i])*(a[i] - b[i])
	return c

def look_parent(i,j):
	global parent
	if (parent[i][j] != (i,j)):
			parent[i][j] = look_parent(parent[i][j][0], parent[i][j][1])
	return parent[i][j]

def main(filein, fileout, radius=3, treshold=150):
	global img_row
	global img_col
	global parent
	global time_start

	# opening image
	img = Image.open(filein)
	img_row = img.size[1]
	img_col = img.size[0]

	in_pixels = list(img.getdata())
	nodes = [[(0,0,0) for x in range(img_col)] for x in range(img_row)]
	edges = []

	# creating nodes
	for i in range(len(in_pixels)):
			row = i // img_col
			col = i % img_col
			nodes[row][col] = in_pixels[i]
	print('[%7.3f] %d nodes are made' % (time.time() - time_start, img_row*img_col))

	# creating edge list
	dx = [0,1,-1,0]
	dy = [1,0,0,-1]
	for i in range(img_row):
			for j in range(img_col):
					for k in range(4):
						for cx in range(1,radius+1):
							for cy in range(1,radius+1):
									ni = i+cx*dx[k]
									nj = j+cy*dy[k]
									if (valid(ni, nj)):
											edges.append((jarak(nodes[i][j],nodes[ni][nj]), (ni,nj), (i,j)))
	print('[%7.3f] %d edges made' %(time.time() - time_start, len(edges)))

	# sorting edge based on distance
	edges.sort(key=lambda tup: tup[0])
	print('[%7.3f] edges are sorted' % (time.time() - time_start))

	# disjoint set initialization
	parent = [[(i,j) for j in range(img_col)] for i in range(img_row)]

	# run mst until treshold
	edges_taken = 0
	i = 0
	while(edges_taken < img_row*img_col-1 and edges[i][0] <= treshold):
			ce = edges[i]
			pce1 = look_parent(ce[1][0], ce[1][1])
			pce2 = look_parent(ce[2][0], ce[2][1])
			if (pce1 != pce2):
							parent[pce1[0]][pce1[1]] = pce2
							edges_taken+=1
			i+=1
	print('[%7.3f] mst is made with %d edges' % (time.time() - time_start, edges_taken))

	# add all set to list
	parent_list = []
	for i in range(img_row):
		for j in range(img_col):
			if (parent[i][j] == (i,j)):
				parent_list.append((i,j))

	# assign every pixel to its set
	parent_i = [[0 for i in range(img_col)] for j in range(img_row)]
	for i in range(img_row):
		for j in range(img_col):
			target = look_parent(i,j)
			min_i = 0
			max_i = len(parent_list)-1
			mid_i = 0
			while (min_i < max_i):
				mid_i = (min_i+max_i)//2
				if (parent_list[mid_i] == target):
					break
				elif (parent_list[mid_i] < target):
					min_i = mid_i+1
				else:
					max_i = mid_i
			parent_i[i][j] = mid_i
	print('[%7.3f] %d parent listed' %(time.time() - time_start, len(parent_list)))
	
	# count average every set
	parsum = [(0,0,0) for i in range(len(parent_list))]
	parcnt = [0 for i in range(len(parent_list))]
	for i in range(img_row):
		for j in range(img_col):
			pari = parent_i[i][j]
			parcnt[pari] += 1
			parsum[pari] = (parsum[pari][0] + nodes[i][j][0],parsum[pari][1] + nodes[i][j][1],parsum[pari][2] + nodes[i][j][2])
	print('[%7.3f] average counted' % (time.time()-time_start))

	# replace all pixel with its set's average
	for i in range(img_row):
		for j in range(img_col):
			pari = parent_i[i][j]
			nodes[i][j] = (
				parsum[pari][0]//parcnt[pari],
				parsum[pari][1]//parcnt[pari],
				parsum[pari][2]//parcnt[pari]
			)
	print('[%7.3f] replaced'%(time.time()-time_start))

	# creating output
	out_pixels = []
	for i in range(len(in_pixels)):
			row = i // img_col
			col = i % img_col
			out_pixels.append(nodes[row][col])
	print('[%7.3f] out pixels are made' % (time.time()-time_start))

	img.show()

	out_img = Image.new(img.mode, img.size)
	out_img.putdata(out_pixels)
	out_img.save(fileout)
	out_img.show()

if __name__ == '__main__':
	time_start = time.time()
	if (len(sys.argv) <= 3):
		main(sys.argv[1], sys.argv[2])
	else:
		main(sys.argv[1], sys.argv[2], treshold=int(sys.argv[3]))
